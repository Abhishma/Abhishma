import json
from pathlib import Path

from core import AgentRunner, FakeClient, fake_text, fake_tool_call
from solutions.po_to_order import handlers as po
from solutions.po_to_order.validate import check_order, schema_errors
from solutions.support_wismo import handlers as sw
from solutions.sync_exception import handlers as sx
from solutions.sync_exception.triage import classify_failure, suggest_fix

PO_FIX = Path(__file__).resolve().parent.parent / "solutions" / "po_to_order" / "fixtures"

# ------------------------------------------------------------ support_wismo


def test_lookup_requires_matching_email():
    assert sw.lookup_order("#1042", "wrong@example.com")["found"] is False
    o = sw.lookup_order("1042", "Jordan.Lee@example.com")
    assert o["found"] and o["fulfillment_status"] == "unfulfilled"
    assert "email" not in o


def test_tracking():
    assert sw.get_tracking("#1042")["shipped"] is False
    assert sw.get_tracking("#1018")["status"] == "delivered"


def test_return_rules_final_sale_window_fee():
    r = sw.start_return("#1018", ["LI-1", "LI-2"], "too_small")
    assert r["created"] and r["accepted"] == ["LI-1"] and r["rejected"][0]["reason"] == "final sale"
    assert r["label_fee"] == 7.95
    assert sw.start_return("#1018", ["LI-1"], "damaged")["label_fee"] == 0.0
    late = sw.start_return("#0977", ["LI-1"], "changed_mind")
    assert late["created"] is False and "window" in late["error"]
    assert sw.start_return("#1042", ["LI-1"], "too_small")["created"] is False


def test_exchange_stock_check():
    assert sw.offer_exchange("#1018", "LI-1", "TH-BOOT-BRN-10.5")["available"] is True
    assert sw.offer_exchange("#1018", "LI-1", "TH-BOOT-BRN-11")["available"] is False
    assert sw.offer_exchange("#1018", "LI-9", "TH-BOOT-BRN-10.5")["available"] is False


def test_edit_address_direct_rules():
    assert sw.edit_order_address("#1018", "1 A St", "Toronto", "ON", "M5H 1J9", "CA")["updated"] is False
    assert sw.edit_order_address("#1042", "1 A St", "Vancouver", "BC", "V6B", "CA")["updated"] is False
    assert sw.edit_order_address("#1042", "455 Oak Ave", "Portland", "OR", "97205", "US")["updated"] is True


def test_edit_address_is_gated_by_runner():
    client = FakeClient([
        fake_tool_call("lookup_order", {"order_number": "#1042", "email": "jordan.lee@example.com"}),
        fake_tool_call("edit_order_address", {"order_number": "#1042", "address1": "455 Oak Ave", "city": "Portland",
                                              "province_code": "OR", "zip": "97205", "country_code": "US"}),
        fake_tool_call("add_ticket_note", {"ticket_id": "T-1", "note": "INTENT: address change | PENDING: approval"}),
        fake_text("I have requested the address change; our team will confirm shortly."),
    ])
    runner = AgentRunner("support_wismo", client)
    result = runner.run("Please send #1042 to 455 Oak Ave", context={"ticket_id": "T-1"})
    assert sw.STATE["address_edits"] == []
    assert len(result.pending_approvals) == 1
    assert sw.STATE["notes"][0]["ticket_id"] == "T-1"
    runner.approve(result.pending_approvals[0]["approval_id"])
    assert sw.STATE["address_edits"][0]["new"]["address1"] == "455 Oak Ave"


def test_escalate():
    assert sw.escalate("T-9", "lost_package", "high")["queue"] == "tier2"
    assert sw.escalate("T-9", "chargeback_threat", "urgent")["queue"] == "lead"


# ----------------------------------------------------------- sync_exception


def test_classify_all_fixture_failures():
    got = {r["sync_id"]: classify_failure(r) for r in sx.DATA["failed_syncs"]}
    assert got == {
        "SYN-001": "missing_sku", "SYN-002": "missing_sku", "SYN-003": "duplicate_order",
        "SYN-004": "address_error", "SYN-005": "tax_error", "SYN-006": "inventory_mismatch",
        "SYN-007": "payout_mismatch", "SYN-008": "transient", "SYN-009": "tax_error",
    }
    assert classify_failure({"error": "Something odd happened"}) == "unknown"


def test_suggested_fixes_and_safety():
    recs = {r["sync_id"]: r["triage"] for r in sx.list_failed_syncs()["records"]}
    assert recs["SYN-001"] == {"cause": "missing_sku", "fix": "trim_sku_whitespace", "safe": True,
                               "detail": "'TEA-GREEN-100G ' -> 'TEA-GREEN-100G'"}
    assert recs["SYN-002"]["fix"] == "map_sku" and not recs["SYN-002"]["safe"]
    assert "MUG-STONE-BLUE" in recs["SYN-002"]["detail"]
    assert recs["SYN-004"]["fix"] == "normalize_country_code" and recs["SYN-004"]["safe"]
    assert recs["SYN-005"]["fix"] == "round_tax_2dp"
    assert recs["SYN-009"]["fix"] is None and "accountant" in recs["SYN-009"]["detail"]
    assert recs["SYN-006"]["safe"] is False


def test_safe_retry_resolves_and_filters():
    assert sx.retry_sync("SYN-001", "trim_sku_whitespace")["success"]
    ids = [r["sync_id"] for r in sx.list_failed_syncs()["records"]]
    assert "SYN-001" not in ids
    assert sx.list_failed_syncs(erp="xero")["count"] == 2


def test_unsafe_fix_returns_pending_and_approval_applies():
    res = sx.retry_sync("SYN-006", "transfer_stock_from_sydney")
    assert res["status"] == "pending_approval"
    applied = sx.retry_sync("SYN-006", "transfer_stock_from_sydney", approved=True)
    assert applied["success"]


def test_map_sku_then_retry():
    assert sx.retry_sync("SYN-002")["success"] is False
    assert sx.map_sku("MUG-STONE-BLU", "NOPE")["mapped"] is False
    assert sx.map_sku("MUG-STONE-BLU", "MUG-STONE-BLUE")["mapped"]
    assert sx.get_erp_item("MUG-STONE-BLU")["found"]
    assert sx.retry_sync("SYN-002")["success"]


def test_sync_runner_gates_map_sku_and_handler_pending():
    client = FakeClient([
        fake_tool_call("list_failed_syncs", {}),
        fake_tool_call("map_sku", {"shopify_sku": "MUG-STONE-BLU", "erp_code": "MUG-STONE-BLUE"}),
        fake_tool_call("retry_sync", {"sync_id": "SYN-006", "fix": "transfer_stock"}),
        fake_tool_call("post_slack", {"channel": "#ops", "text": "Sync exceptions: 9 failed, 0 fixed, 2 awaiting approval"}),
        fake_text("Posted summary."),
    ])
    runner = AgentRunner("sync_exception", client)
    result = runner.run("Run the morning triage")
    assert len(result.pending_approvals) == 2
    assert sx.STATE["mappings"] == {}
    assert sx.STATE["slack"][0]["channel"] == "#ops"
    # approving the handler-level pending runs it with approved=True
    second = next(p for p in result.pending_approvals if p["tool"] == "retry_sync")
    assert runner.approve(second["approval_id"])["success"]


def test_post_slack_length_guard():
    assert sx.post_slack("#ops", "x" * 4000)["posted"] is False


# --------------------------------------------------------------- po_to_order


def _extracted(mid):
    return json.loads((PO_FIX / "extracted" / f"{mid}.json").read_text())


def test_extracted_fixtures_match_schema():
    for mid in ("MSG-1001", "MSG-1002"):
        assert schema_errors(_extracted(mid), po.ORDER_SCHEMA) == []


def test_schema_errors_detected():
    bad = _extracted("MSG-1001")
    bad.pop("po_number")
    bad["lines"][0]["quantity"] = "24"
    bad["surprise"] = 1
    errs = schema_errors(bad, po.ORDER_SCHEMA)
    assert any("po_number" in e for e in errs)
    assert any("quantity" in e for e in errs)
    assert any("surprise" in e for e in errs)
    assert schema_errors({**_extracted("MSG-1001"), "lines": []}, po.ORDER_SCHEMA)


def test_validation_harbour_cafes():
    r = po.validate_order("CUST-HCG", _extracted("MSG-1001"))
    codes = {d["code"] for d in r["discrepancies"]}
    assert codes == {"price_mismatch", "stated_subtotal_mismatch", "credit_limit"}
    assert r["totals"]["subtotal"] == 647.0 and r["totals"]["tax"] == 64.7
    assert r["can_create_draft"] is True


def test_validation_bergcafe_blocks():
    r = po.validate_order("CUST-BERG", _extracted("MSG-1002"))
    codes = {d["code"]: d["severity"] for d in r["discrepancies"]}
    assert codes == {"pack_multiple": "review", "unknown_sku": "block", "terms_mismatch": "review"}
    assert r["can_create_draft"] is False
    assert po.create_draft_order("CUST-BERG", _extracted("MSG-1002"))["created"] is False


def test_check_order_moq_uom_currency_shipto():
    cust = po.CUSTOMERS["CUST-HCG"]
    pl = po.PRICE_LISTS["AU-WHOLESALE-A"]
    order = {**_extracted("MSG-1001"), "currency": "NZD", "ship_to_address": "1 Unknown Rd, Perth WA",
             "lines": [{"sku": "GL-OAT-1L", "description": "oat", "quantity": 6, "uom": "carton", "unit_price": 3.90}]}
    codes = {d["code"] for d in check_order(order, cust, pl)["discrepancies"]}
    assert {"currency_mismatch", "below_moq", "pack_multiple", "uom_mismatch", "unknown_ship_to"} <= codes


def test_customer_lookup_and_document():
    assert po.get_customer(email="mia@harbourcafes.com.au")["customer_id"] == "CUST-HCG"
    assert "balance_owing" not in po.get_customer(email="mia@harbourcafes.com.au")
    assert po.get_customer(email="x@unknown.com")["found"] is False
    doc = po.get_po_document("MSG-1001")
    assert "45512" in doc["text"] and doc["from"] == "purchasing@harbourcafes.com.au"


def test_po_runner_gates_draft():
    order = _extracted("MSG-1001")
    client = FakeClient([
        fake_tool_call("get_po_document", {"message_id": "MSG-1001"}),
        fake_tool_call("validate_order", {"customer_id": "CUST-HCG", "order": order}),
        fake_tool_call("create_draft_order", {"customer_id": "CUST-HCG", "order": order}),
        fake_text("PO 45512: draft pending approval."),
    ])
    runner = AgentRunner("po_to_order", client)
    result = runner.run("Process MSG-1001")
    assert po.STATE["drafts"] == [] and len(result.pending_approvals) == 1
    out = runner.approve(result.pending_approvals[0]["approval_id"])
    assert out["created"] and out["status"] == "draft"
