import pytest

from core import AgentRunner, FakeClient, fake_text, fake_tool_call
from solutions.receptionist import handlers as rc
from solutions.whatsapp_commerce import handlers as wa
from solutions.whatsapp_commerce.national_address import (
    normalize_short_address, validate_full_address, validate_short_address,
)

# ------------------------------------------------------------- receptionist


def test_service_area_and_canadian_fsa():
    assert rc.get_service_area("coolbreeze_ac", "4064")["in_service_area"] is True
    assert rc.get_service_area("coolbreeze_ac", "2000")["in_service_area"] is False
    assert rc.get_service_area("maple_dental", "m5v 2t6")["in_service_area"] is True


def test_price_guide_only_returns_approved_prices():
    ok = rc.get_price_guide("coolbreeze_ac", "aircon_service")
    assert ok["found"] and ok["from"] == 149 and ok["to"] == 199
    missing = rc.get_price_guide("coolbreeze_ac", "ducted_install")
    assert missing["found"] is False and "Do not estimate" in missing["instruction"]


def test_availability_booking_and_double_booking():
    slots = rc.check_availability("coolbreeze_ac", "aircon_install_split_2_5kw")["slots"]
    assert [s["slot_id"] for s in slots] == ["cb-2026-10-19-1300"]
    job = rc.book_job("coolbreeze_ac", "cb-2026-10-19-1300", "Sam", "+61412345678", "1 Given Tce, Paddington",
                      "aircon_install_split_2_5kw")
    assert job["booked"] and job["job_id"].startswith("JOB-")
    again = rc.book_job("coolbreeze_ac", "cb-2026-10-19-1300", "Al", "+61412345679", "x", "aircon_install_split_2_5kw")
    assert again["booked"] is False
    assert rc.check_availability("coolbreeze_ac", "aircon_install_split_2_5kw")["slots"] == []
    wrong = rc.book_job("coolbreeze_ac", "cb-2026-10-20-0800", "Al", "+61412345679", "x", "aircon_service")
    assert wrong["booked"] is False


def test_sms_validation_and_business_name():
    bad = rc.send_sms("coolbreeze_ac", "0412345678", "hi")
    assert bad["sent"] is False
    sent = rc.send_sms("coolbreeze_ac", "+61412345678", "Booked for Monday 8-10am.")
    assert sent["sent"] and sent["body"].startswith("CoolBreeze Air Conditioning:")
    assert rc.send_sms("coolbreeze_ac", "+61412345678", "x" * 500)["sent"] is False


def test_lead_and_transfer():
    assert rc.create_lead("kiez_elektro", "Anna", "+4915112345678", "Steckdose defekt")["created"]
    tr = rc.transfer_to_human("kiez_elektro", "emergency", "emergency", "Brandgeruch")
    assert tr["transferred"] and rc.STATE["transfers"][0]["to"] == "+49301234500"


def test_receptionist_emergency_flow_with_runner():
    client = FakeClient([
        fake_tool_call("transfer_to_human", {"business_id": "coolbreeze_ac", "reason": "emergency",
                                             "urgency": "emergency", "summary": "burning smell from switchboard"}),
        fake_text("Please stay away from the switchboard. Putting you through now."),
    ])
    result = AgentRunner("receptionist", client).run("There's a burning smell from the switchboard",
                                                       context={"business_id": "coolbreeze_ac"})
    assert result.tool_calls[0]["status"] == "ok"
    assert rc.STATE["transfers"][0]["urgency"] == "emergency"
    assert "AI" in client.calls[0]["system"] and "Article 50" in client.calls[0]["system"]


# --------------------------------------------------------- national address


@pytest.mark.parametrize("raw,norm", [
    ("RRRD2929", "RRRD2929"), ("rrrd 2929", "RRRD2929"), ("RRRD-2929", "RRRD2929"),
    ("rrrd٢٩٢٩", "RRRD2929"), ("  mjaa1234 ", "MJAA1234"),
])
def test_short_address_valid(raw, norm):
    r = validate_short_address(raw)
    assert r["valid"] and r["normalized"] == norm


@pytest.mark.parametrize("raw,fragment", [
    ("RRR2929", "8 characters"), ("RRRD29290", "8 characters"), ("2929RRRD", "4 letters followed"),
    ("RR1D2929", "4 letters followed"), ("RRRD0000", "0000"), ("", "empty"), ("ررر2929", "Arabic letters"),
])
def test_short_address_invalid(raw, fragment):
    r = validate_short_address(raw)
    assert not r["valid"] and any(fragment in e for e in r["errors"])


def test_region_hint_and_full_address():
    assert validate_short_address("RRRD2929")["region_hint"] == "Riyadh"
    assert validate_short_address("ZZZZ1234")["region_hint"] is None
    assert validate_full_address("2929", "12345", "7788")["valid"]
    assert not validate_full_address("292", "1234")["valid"]
    assert normalize_short_address("ab.cd 12-34") == "ABCD1234"


# ---------------------------------------------------------- whatsapp handlers


def test_get_order_minimises_data():
    o = wa.get_order(phone="+966501234567")
    assert o["order_id"] == "SA-50121"
    assert "phone" not in o and "short_address" not in o
    assert o["phone_masked"].startswith("+966") and "*" in o["phone_masked"]
    assert o["prepay_incentive"]


def test_confirm_cod_flow():
    assert wa.confirm_cod("SA-50121", True)["status"] == "confirmed"
    assert wa.confirm_cod("SA-50121", True)["updated"] is False
    assert wa.confirm_cod("SA-49910", True)["updated"] is False  # Tabby order


def test_update_address_validates_and_blocks_shipped():
    bad = wa.update_address("SA-50121", "RRD2929")
    assert bad["updated"] is False
    ok = wa.update_address("SA-50121", "rrrd 2929", notes="Near the mosque gate")
    assert ok["updated"] and ok["short_address"] == "RRRD2929"
    assert wa.update_address("SA-50088", "MJAA1234")["updated"] is False


def test_tracking_and_failed_delivery():
    t = wa.get_tracking("SA-50088")
    assert t["shipped"] and t["needs_attention"]
    assert wa.get_tracking("SA-50121")["shipped"] is False


def test_returns_policy_window_and_hygiene():
    r = wa.create_return("SA-49910", ["BKH-01", "OIL-12"], "changed_mind")
    assert r["created"] and r["accepted"] == ["BKH-01"]
    assert r["rejected"][0]["sku"] == "OIL-12"
    assert "Tabby" in r["refund_to"]
    assert wa.create_return("SA-50088", ["AMB-100"], "damaged")["created"] is False


def test_return_outside_window(monkeypatch):
    monkeypatch.setenv("MARGINWISE_NOW", "2026-10-30T12:00:00+03:00")
    r = wa.create_return("SA-49910", ["BKH-01"], "changed_mind")
    assert r["created"] is False and "return window" in r["error"]


def test_handoff_returns_ramadan_hours():
    h = wa.handoff_to_agent("SA-50088", "complaint", "Angry about delay", "ar")
    assert h["handed_off"] and "Ramadan" in h["ramadan_hours"]


def test_whatsapp_runner_validates_before_update():
    client = FakeClient([
        fake_tool_call("validate_national_address", {"short_address": "rrrd 2929"}),
        fake_tool_call("update_address", {"order_id": "SA-50121", "short_address": "RRRD2929"}),
        fake_text("Saved RRRD2929."),
    ])
    result = AgentRunner("whatsapp_commerce", client).run("my code is rrrd 2929",
                                                            context={"sender_phone": "+966501234567"})
    assert [c["name"] for c in result.tool_calls] == ["validate_national_address", "update_address"]
    assert wa.STATE["orders"]["SA-50121"]["short_address"] == "RRRD2929"
    # the sender phone in the transcript is redacted
    assert "+966501234567" not in str(result.transcript)
