import json
from datetime import date
from pathlib import Path

import pytest

from core import AgentRunner, FakeClient, fake_text, fake_tool_call
from solutions.aeo_visibility import handlers as aeo
from solutions.aeo_visibility.adapters import AnthropicAdapter, FixtureAdapter, OpenAIAdapter, PerplexityAdapter
from solutions.aeo_visibility.harness import build_questions, run
from solutions.aeo_visibility.parser import Mention, mention_points, parse_answer, share_of_voice
from solutions.lead_triage import handlers as lt
from solutions.lead_triage.scoring import check_consent
from solutions.quote_builder import handlers as qb
from solutions.quote_builder.quote import validate_angebot

AEO_FIX = Path(__file__).resolve().parent.parent / "solutions" / "aeo_visibility" / "fixtures"
BRANDS = json.loads((AEO_FIX / "brands.json").read_text())["brands"]
ANSWERS = json.loads((AEO_FIX / "answers.json").read_text())

# ------------------------------------------------------------ AEO parser


def _by_brand(mentions):
    return {m.brand: m for m in mentions}


def test_numbered_list_ranks_and_positions():
    ms = _by_brand(parse_answer(ANSWERS["anthropic"]["ls_best"], BRANDS))
    assert ms["Polar Air Services"].list_rank == 1 and ms["Polar Air Services"].position == 1
    assert ms["CoolBreeze Air Conditioning"].list_rank == 2
    assert ms["Brisbane Climate Co"].list_rank == 3
    assert "Arctic Breeze Services" not in ms


def test_bullets_and_aliases():
    ms = _by_brand(parse_answer(ANSWERS["openai"]["ls_best"], BRANDS))
    assert ms["Brisbane Climate Co"].list_rank == 1
    assert ms["Polar Air Services"].list_rank == 2  # alias "Polar Air"
    assert ms["Arctic Breeze Services"].list_rank == 3  # alias "Arctic Breeze"


def test_prose_mentions_sentiment_and_counts():
    ms = _by_brand(parse_answer(ANSWERS["anthropic"]["ls_recommend"], BRANDS))
    assert ms["CoolBreeze Air Conditioning"].position == 1 and ms["CoolBreeze Air Conditioning"].list_rank is None
    assert ms["CoolBreeze Air Conditioning"].sentiment == "positive"
    neg = _by_brand(parse_answer(ANSWERS["openai"]["ls_recommend"], BRANDS))
    assert neg["Brisbane Climate Co"].sentiment == "negative"
    assert mention_points(neg["Brisbane Climate Co"]) == 0.0


def test_no_mentions_and_word_boundaries():
    assert parse_answer(ANSWERS["perplexity"]["ls_emergency"], BRANDS) == []
    assert parse_answer("We love CoolBreezeX and Polar Airways", BRANDS) == []
    assert parse_answer("", BRANDS) == []


def test_case_insensitive_and_count():
    ms = _by_brand(parse_answer("coolbreeze is great. I'd call COOLBREEZE first.", BRANDS))
    assert ms["CoolBreeze Air Conditioning"].count == 2


def test_points():
    assert mention_points(Mention("a", 1, 1, 1, "positive", "")) == 1.0
    assert mention_points(Mention("a", 2, 3, 1, "positive", "")) == pytest.approx(1 / 3)
    assert mention_points(Mention("a", 2, None, 1, "neutral", "")) == 0.25


def test_share_of_voice_on_fixtures():
    out = aeo.run_visibility_check("local_service", {"category": "air conditioning installer",
                                                     "city": "Brisbane", "country": "Australia"})
    table = {r["brand"]: r for r in out["score"]["brands"]}
    assert out["answers"] == 9
    assert table["Polar Air Services"]["share_of_voice_pct"] == 37.5
    assert table["CoolBreeze Air Conditioning"]["share_of_voice_pct"] == 26.0
    assert table["Brisbane Climate Co"]["negative_mentions"] == 1
    assert round(sum(r["share_of_voice_pct"] for r in table.values())) == 100
    assert out["score"]["by_assistant"]["perplexity"]["CoolBreeze Air Conditioning"] == 44.4
    stored = aeo.get_share_of_voice(out["run_id"], include_answers=True)
    assert stored["found"] and len(stored["answers"]) == 9


def test_share_of_voice_empty():
    s = share_of_voice([], BRANDS)
    assert s["answers"] == 0 and all(r["share_of_voice_pct"] == 0 for r in s["brands"])


def test_build_questions_placeholders():
    qs = build_questions("local_service", "en", category="plumber", city="Toronto", country="Canada")
    assert qs[0]["question"] == "Who is the best plumber in Toronto?"
    with pytest.raises(KeyError):
        build_questions("ecommerce_product", "en", product="running shoes")
    assert "Muenchen" in build_questions("local_service", "de", category="Elektriker", city="Muenchen")[0]["question"]


def test_stub_adapters_reported_as_errors():
    qs = build_questions("local_service", "en", category="x", city="y", country="z")[:1]
    out = run(qs, [OpenAIAdapter(), PerplexityAdapter(), FixtureAdapter("anthropic")], BRANDS)
    assert {e["assistant"] for e in out["errors"]} == {"openai", "perplexity"}
    assert len(out["results"]) == 1


def test_anthropic_adapter_with_fake_client():
    client = FakeClient([fake_text("1. Polar Air Services\n2. CoolBreeze")])
    text = AnthropicAdapter(client).ask("Who is the best installer?", {"country_code": "AU", "city": "Brisbane"})
    assert "Polar Air" in text
    tool = client.calls[0]["tools"][0]
    assert tool["type"] == "web_search_20260209" and tool["user_location"]["country"] == "AU"


# ------------------------------------------------------------ lead triage


def test_lead_scores_and_tiers():
    tiers = {lid: lt.score_lead(lid)["tier"] for lid in lt.LEADS}
    assert tiers == {"L-1001": "A", "L-1002": "A", "L-1003": "C", "L-1004": "A", "L-1005": "DQ"}
    assert lt.score_lead("L-1001")["score"] == 100
    assert any("free email" in r for r in lt.score_lead("L-1003")["reasons"])


def test_routing():
    assert lt.assign_owner("L-1002", "A")["owner_id"] == "owner_lena"
    assert lt.assign_owner("L-1004", "A")["owner_id"] == "owner_daniel"
    assert lt.assign_owner("L-1003", "C")["owner_id"] == "nurture_queue"
    assert lt.assign_owner("L-1005", "DQ")["assigned"] is False


@pytest.mark.parametrize("lead_id,email_type,allowed", [
    ("L-1001", "inquiry_response", True),
    ("L-1001", "marketing_followup", False),   # AU, no consent
    ("L-1002", "inquiry_response", True),
    ("L-1002", "marketing_followup", False),   # DE, opt-in but no double opt-in
    ("L-1003", "inquiry_response", False),     # newsletter signup, nothing to answer
    ("L-1003", "marketing_followup", True),    # US CAN-SPAM opt-out model
    ("L-1004", "marketing_followup", True),    # CA implied consent from 2-day-old inquiry
])
def test_consent_matrix(lead_id, email_type, allowed):
    assert check_consent(lt.LEADS[lead_id], email_type, date(2026, 10, 17))["allowed"] is allowed


def test_casl_implied_consent_expires():
    lead = {**lt.LEADS["L-1004"], "consent": {"marketing_opt_in": False, "inquiry_date": "2026-01-01"}}
    assert check_consent(lead, "marketing_followup", date(2026, 10, 17))["allowed"] is False


def test_de_double_opt_in_allows_marketing_and_us_needs_address():
    lead = {**lt.LEADS["L-1002"], "consent": {"marketing_opt_in": True, "double_opt_in_confirmed": True}}
    assert check_consent(lead, "marketing_followup", date(2026, 10, 17))["allowed"]
    us = check_consent(lt.LEADS["L-1003"], "marketing_followup", date(2026, 10, 17))
    assert "physical postal address" in us["required_elements"]


def test_draft_email_checks():
    assert lt.draft_email("L-1001", "marketing_followup", "s", "b")["drafted"] is False
    assert lt.draft_email("L-1003", "marketing_followup", "s", "no opt out line")["drafted"] is False
    assert lt.draft_email("L-1003", "marketing_followup", "s", "Unsubscribe here")["drafted"] is True
    assert lt.draft_email("L-1001", "inquiry_response", "Re: WISMO", "Hi Sophie")["drafted"] is True


def test_lead_runner_gates_draft_email():
    client = FakeClient([
        fake_tool_call("get_lead", {"lead_id": "L-1001"}),
        fake_tool_call("score_lead", {"lead_id": "L-1001"}),
        fake_tool_call("assign_owner", {"lead_id": "L-1001", "tier": "A"}),
        fake_tool_call("draft_email", {"lead_id": "L-1001", "email_type": "inquiry_response",
                                       "subject": "Cutting your WISMO tickets", "body": "Hi Sophie ..."}),
        fake_tool_call("log_activity", {"lead_id": "L-1001", "activity_type": "triage", "summary": "100 A Priya"}),
        fake_text("TRIAGE L-1001: score 100 tier A owner Priya Sharma"),
    ])
    result = AgentRunner("lead_triage", client).run("New lead L-1001")
    assert lt.STATE["drafts"] == [] and len(result.pending_approvals) == 1
    assert lt.STATE["assignments"]["L-1001"] == "owner_priya"
    # lead email is redacted in the stored transcript
    assert "sophie@kindredskin.com.au" not in json.dumps(result.transcript)


# ----------------------------------------------------------- quote builder


def test_quote_ranges_and_gst():
    q = qb.calculate_quote("sunstate_air", [
        {"item_id": "aircon_split_install_2_5kw", "quantity": 1,
         "answers": {"room_size_m2": 20, "wall_type": "brick", "storeys": 1}},
        {"item_id": "aircon_extra_pipe_m", "quantity": 2}])
    assert q["ok"] and (q["subtotal_low"], q["subtotal_high"]) == (1580.0, 1920.0)
    assert (q["total_low"], q["total_high"]) == (1738.0, 2112.0)
    assert q["missing_answers"] == [] and q["requires_site_visit"] is False


def test_quote_min_charge_missing_answers_site_visit_unknown():
    q = qb.calculate_quote("sunstate_air", [{"item_id": "roof_tile_replace", "quantity": 3}])
    assert (q["subtotal_low"], q["subtotal_high"]) == (280.0, 280.0)
    assert q["total_low"] == 308.0
    assert q["missing_answers"][0]["questions"] == ["roof_type", "storeys"]
    assert qb.calculate_quote("sunstate_air", [{"item_id": "aircon_ducted", "quantity": 1}])["requires_site_visit"]
    assert qb.calculate_quote("sunstate_air", [{"item_id": "solar", "quantity": 1}])["ok"] is False
    assert qb.calculate_quote("sunstate_air", [{"item_id": "roof_tile_replace", "quantity": 0}])["ok"] is False


def test_estimate_document():
    q = qb.calculate_quote("sunstate_air", [{"item_id": "elec_led_downlight", "quantity": 6,
                                             "answers": {"ceiling_access": "yes"}}])
    d = qb.create_quote_document("sunstate_air", q["quote_id"], "Tom Lee", "3 Bay St, Southport QLD")
    doc = d["document"]
    assert d["ok"] and doc["doc_type"] == "estimate" and doc["total_range"] == [429.0, 594.0]
    assert doc["number"] == "EST-2026-0001" and doc["valid_until"] == "2026-11-16"
    assert qb.create_quote_document("sunstate_air", q["quote_id"], "Tom", "x", "angebot")["ok"] is False


def test_german_angebot_mandatory_fields():
    q = qb.calculate_quote("meister_elektro", [{"item_id": "steckdose_neu", "quantity": 3, "answers": {"wandart": "Beton"}},
                                               {"item_id": "anfahrt", "quantity": 1}])
    d = qb.create_quote_document("meister_elektro", q["quote_id"], "Anna Schmidt",
                                 "Leopoldstrasse 1, 80802 Muenchen", "angebot")
    doc = d["document"]
    assert d["ok"] and d["problems"] == []
    assert doc["angebotsnummer"] == "AN-2026-0001" and doc["datum"] == "17.10.2026" and doc["gueltig_bis"] == "16.11.2026"
    assert (doc["netto_summe"], doc["ust_satz"], doc["ust_betrag"], doc["brutto_summe"]) == (330.0, 19.0, 62.7, 392.7)
    assert doc["anbieter"]["steuer_id"] == "DE298765432"
    broken = {**doc, "kunde": {"name": "", "anschrift": None}, "brutto_summe": 400}
    problems = validate_angebot(broken)
    assert any("kunde.name" in p for p in problems) and any("brutto" in p for p in problems)


def test_angebot_refused_for_ranges():
    q = qb.calculate_quote("meister_elektro", [{"item_id": "zaehlerschrank_neu", "quantity": 1,
                                                "answers": {"baujahr": 1970, "anzahl_zaehler": 2}}])
    d = qb.create_quote_document("meister_elektro", q["quote_id"], "A", "B", "angebot")
    assert d["ok"] is False and "fixed prices" in d["error"]


def test_site_visit_booking():
    slots = qb.check_site_visit_slots("sunstate_air")["slots"]
    b = qb.book_site_visit("sunstate_air", slots[0]["slot_id"], "Tom", "+61412000000", "3 Bay St")
    assert b["booked"]
    assert qb.book_site_visit("sunstate_air", slots[0]["slot_id"], "X", "+61412000001", "y")["booked"] is False
    assert len(qb.check_site_visit_slots("sunstate_air")["slots"]) == len(slots) - 1
