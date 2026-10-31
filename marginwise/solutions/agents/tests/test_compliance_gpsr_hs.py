from decimal import Decimal

import pytest

from core import AgentRunner, FakeClient, fake_text, fake_tool_call
from solutions.compliance_copy_auditor import handlers as cc
from solutions.compliance_copy_auditor.rules import DISCLAIMER, scan
from solutions.gpsr_extractor import handlers as gp
from solutions.gpsr_extractor.gpsr import rule_based_extract, to_metafields, validate_fields
from solutions.hs_classifier import handlers as hs
from solutions.hs_classifier.landed_cost import USFees, calculate_landed_cost

# ------------------------------------------------------------ compliance


def _ids(text, markets, channel="web"):
    return {f["rule_id"] for f in scan(text, markets, channel)}


def test_empco_claims_detected():
    ids = _ids(cc.COPY["DE-PDP-001"]["text"], ["DE"])
    assert {"EMPCO_CLIMATE_NEUTRAL", "EMPCO_GENERIC_CLAIM", "EMPCO_SELF_LABEL", "PANGV_PRICE_REDUCTION"} <= ids


def test_pangv_suppressed_when_30_day_reference_present():
    assert _ids(cc.COPY["DE-PDP-002"]["text"], ["DE"]) == set()


def test_meta_rules_only_for_meta_channel():
    text = cc.COPY["META-AD-014"]["text"]
    assert {"META_UNREALISTIC_OUTCOME", "META_PERSONAL_ATTRIBUTES"} <= _ids(text, ["US"], "meta_ad")
    assert not _ids(text, ["US"], "web") & {"META_UNREALISTIC_OUTCOME", "META_PERSONAL_ATTRIBUTES"}


def test_au_drip_pricing_and_market_filter():
    text = cc.COPY["AU-LP-007"]["text"]
    hits = scan(text, ["AU"])
    drip = [h for h in hits if h["rule_id"] == "AU_DRIP_PRICING"]
    assert len(drip) == 3 and all(h["risk"] == "high" for h in drip)
    assert "AU_ENVIRONMENTAL_CLAIM" in {h["rule_id"] for h in hits}
    # EmpCo rules do not apply to an AU-only asset
    assert not {h["rule_id"] for h in hits} & {"EMPCO_GENERIC_CLAIM"}
    assert "AU_DRIP_PRICING" not in _ids(text, ["US"])


def test_findings_quote_is_sentence_from_copy():
    text = cc.COPY["DE-PDP-001"]["text"]
    for f in scan(text, ["DE"]):
        assert f["quote"] in text and f["match"] in f["quote"]
        assert f["suggested_rewrite"]


def test_clean_copy_has_no_findings():
    assert scan(cc.COPY["US-EMAIL-003"]["text"], ["US"], "email") == []


def test_record_findings_requires_fields_and_adds_disclaimer():
    assert cc.record_findings("X", [{"quote": "a"}], "low")["recorded"] is False
    ok = cc.record_findings("X", [{"quote": "a", "rule": "r", "risk": "low", "suggested_rewrite": "b"}], "low")
    assert ok["recorded"] and ok["disclaimer"] == DISCLAIMER and "not legal advice" in DISCLAIMER


def test_auditor_runner_end_to_end():
    text = cc.COPY["DE-PDP-001"]["text"]
    client = FakeClient([
        fake_tool_call("get_copy", {"asset_id": "DE-PDP-001"}),
        fake_tool_call("scan_rules", {"text": text, "markets": ["DE"], "channel": "web"}),
        fake_tool_call("record_findings", {"asset_id": "DE-PDP-001", "overall_risk": "high", "findings": [
            {"rule_id": "EMPCO_CLIMATE_NEUTRAL", "quote": "Unsere Bambus-Zahnbuerste ist klimaneutral und 100% umweltfreundlich.",
             "rule": "EmpCo", "risk": "high", "suggested_rewrite": "Griff aus FSC-Bambus."}]}),
        fake_text('{"overall_risk": "high"} Automated pre-screen only. This is not legal advice.'),
    ])
    result = AgentRunner("compliance_copy_auditor", client).run("Audit DE-PDP-001")
    assert cc.STATE["audits"][0]["overall_risk"] == "high"
    assert "not legal advice" in result.final_text


# ----------------------------------------------------------------- GPSR


def test_gpsr_rule_extraction_complete_document():
    fields = gp.get_supplier_document("SUP-DOC-01")["rule_based_fields"]
    assert fields["manufacturer_name"] == "Shenzhen Maple Toys Co., Ltd."
    assert fields["eu_rp_name"] == "EuroSafe Compliance GmbH"
    assert fields["eu_rp_email"] == "eu-rep@eurosafe-compliance.de"
    assert fields["product_identifier"] == "Type WR-7-NAT; Batch LOT 2026-08-B"
    v = validate_fields(fields, ["DE"])
    assert v["complete"] and not v["manufacturer_in_eu"]


def test_gpsr_flags_missing_fields():
    fields = gp.get_supplier_document("SUP-DOC-02")["rule_based_fields"]
    v = validate_fields(fields, ["DE"])
    assert not v["complete"]
    assert {"manufacturer_address", "manufacturer_email", "eu_rp_name", "eu_rp_address",
            "eu_rp_email", "product_identifier", "warnings"} <= set(v["missing"])


def test_gpsr_non_eu_rp_and_bad_email_and_german_warnings():
    fields = {"manufacturer_name": "Acme Ltd", "manufacturer_address": "1 Road, Auckland, New Zealand",
              "manufacturer_email": "WeChat: acme", "eu_rp_name": "UK Rep Ltd",
              "eu_rp_address": "10 Street, London, United Kingdom", "eu_rp_email": "rep@uk.example",
              "product_identifier": "Type A1", "warnings": "Keep away from fire."}
    v = validate_fields(fields, ["DE"])
    probs = " ".join(v["problems"])
    assert "not a valid email" in probs and "not in the EU/EEA" in probs and "German" in probs


def test_gpsr_eu_manufacturer_needs_no_rp():
    fields = {"manufacturer_name": "Holz GmbH", "manufacturer_address": "Weg 1, 10115 Berlin, Germany",
              "manufacturer_email": "info@holz.example", "product_identifier": "Typ H-1",
              "warnings": "Achtung: nicht fuer Kinder unter 3 Jahren geeignet."}
    assert validate_fields(fields, ["DE"])["complete"]


def test_gpsr_german_labels():
    text = "Hersteller: Holz GmbH\nAnschrift: Weg 1, 10115 Berlin, Deutschland\nE-Mail: info@holz.example\n" \
           "Typ: H-1\nCharge: 2026-03\nWarnhinweise: Achtung, Kleinteile."
    f = rule_based_extract(text)
    assert f["manufacturer_name"] == "Holz GmbH" and f["product_identifier"] == "Type H-1; Batch 2026-03"
    assert validate_fields(f, ["DE"])["complete"]


def test_gpsr_metafields_and_gate():
    fields = gp.get_supplier_document("SUP-DOC-01")["rule_based_fields"]
    mf = to_metafields("gid://shopify/Product/8801", fields)["metafields"]
    assert len(mf) == 8 and all(m["namespace"] == "gpsr" for m in mf)
    assert {m["type"] for m in mf if m["key"] == "warnings"} == {"multi_line_text_field"}
    client = FakeClient([fake_tool_call("write_metafields", {"product_id": "gid://shopify/Product/8801", "fields": fields}),
                         fake_text("pending approval")])
    result = AgentRunner("gpsr_extractor", client).run("go")
    assert gp.STATE["written"] == {} and result.pending_approvals


# ------------------------------------------------------- HS + landed cost


def test_hs_search_ranks_expected_codes():
    assert hs.search_hs_nomenclature("cotton knitted t-shirt")["results"][0]["code"] == "6109.10"
    assert hs.search_hs_nomenclature("leather tote handbag")["results"][0]["code"] == "4202.21"
    assert hs.search_hs_nomenclature("bamboo toothbrush")["results"][0]["code"] == "9603.21"
    assert hs.search_hs_nomenclature("zzz")["results"] == []


def test_submit_for_review_validates():
    assert hs.submit_for_review("S", [], "r", ["US"])["submitted"] is False
    assert hs.submit_for_review("S", [{"hs6": "610910", "confidence": 0.9}], "r", ["US"])["submitted"] is False
    assert hs.submit_for_review("S", [{"hs6": "6109.10", "confidence": 1.5}], "r", ["US"])["submitted"] is False
    ok = hs.submit_for_review("S", [{"hs6": "6109.10", "confidence": 0.9}], "r", ["US", "CA"])
    assert ok["status"] == "awaiting_human_review"


def test_landed_cost_canada_example_from_prompt():
    r = calculate_landed_cost(goods_value=4750, fx_rate=1.37, duty_rate_pct=18, destination="CA",
                              freight=300, quantity=500)
    assert r["customs_value"] == "6507.50"  # FOB: freight excluded
    assert r["duty"] == "1171.35"
    assert r["import_tax"] == "383.94"  # 5% GST on value + duty
    assert r["landed_total"] == "8473.79"
    assert r["landed_per_unit"] == "16.95"


def test_landed_cost_us_with_surcharge_mpf_hmf():
    r = calculate_landed_cost(goods_value=10000, fx_rate=1, duty_rate_pct=16.5, destination="US",
                              tariff_surcharge_pct=25, freight=800, mode="ocean")
    assert r["duty"] == "1650.00" and r["tariff_surcharge"] == "2500.00"
    assert r["mpf"] == "34.64"  # 0.3464% of 10,000 (above minimum)
    assert r["hmf"] == "12.50"
    assert r["landed_total"] == str(Decimal("10000") + 800 + Decimal("1650") + 2500 + Decimal("34.64") + Decimal("12.50"))


def test_landed_cost_mpf_min_max_and_informal():
    small = calculate_landed_cost(goods_value=3000, fx_rate=1, duty_rate_pct=0, destination="US")
    assert small["mpf"] == "33.58"  # minimum applies
    big = calculate_landed_cost(goods_value=1_000_000, fx_rate=1, duty_rate_pct=0, destination="US")
    assert big["mpf"] == "651.50"  # maximum applies
    informal = calculate_landed_cost(goods_value=800, fx_rate=1, duty_rate_pct=0, destination="US",
                                     us_fees=USFees(informal_mpf_flat=Decimal("2.69")))
    assert informal["mpf"] == "2.69"
    assert calculate_landed_cost(goods_value=800, fx_rate=1, duty_rate_pct=0, destination="US",
                                 mode="air")["hmf"] == "0.00"


def test_landed_cost_cif_other_and_hst():
    r = calculate_landed_cost(goods_value=100, fx_rate=2, duty_rate_pct=10, destination="OTHER",
                              freight=10, insurance=5, import_tax_pct=10)
    assert r["valuation_basis"] == "CIF" and r["customs_value"] == "230.00"
    assert r["duty"] == "23.00" and r["import_tax"] == "25.30"
    hst = calculate_landed_cost(goods_value=1000, fx_rate=1, duty_rate_pct=0, destination="CA", import_tax_pct=13)
    assert hst["import_tax"] == "130.00"


def test_landed_cost_input_validation():
    with pytest.raises(ValueError):
        calculate_landed_cost(goods_value=100, fx_rate=0, duty_rate_pct=5)
    with pytest.raises(ValueError):
        calculate_landed_cost(goods_value=-1, fx_rate=1, duty_rate_pct=5)
    with pytest.raises(ValueError):
        calculate_landed_cost(goods_value=1, fx_rate=1, duty_rate_pct=5, destination="UK")
    with pytest.raises(ValueError):
        calculate_landed_cost(goods_value=1, fx_rate=1, duty_rate_pct=5, quantity=0)
