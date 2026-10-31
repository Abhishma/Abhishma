"""Mock handlers for PO-to-order extraction.

TODO(adapters):
  - Inbox: Gmail API / Microsoft Graph (messages + attachments); PDF text via
    pdfplumber or the Messages API document block for scanned PDFs
  - Customers / price lists / draft orders: Cin7, Unleashed, NetSuite, MYOB, Xero
    (quotes), QuickBooks (estimates), Shopify B2B (draftOrderCreate), DEAR, Brightpearl
"""

from __future__ import annotations

import uuid
from pathlib import Path

from core.fixtures import load_json, not_found

from .validate import check_order, schema_errors

FIXTURES = Path(__file__).parent / "fixtures"
CUSTOMERS = load_json(FIXTURES / "customers.json")
PRICE_LISTS = load_json(FIXTURES / "price_list.json")
ORDER_SCHEMA = load_json(FIXTURES / "order_schema.json")
STATE: dict[str, list] = {"drafts": [], "flags": []}


def reset_state() -> None:
    for v in STATE.values():
        v.clear()


def get_po_document(message_id: str) -> dict:
    path = FIXTURES / "emails" / f"{message_id}.txt"
    if not path.exists():
        return not_found("message", message_id)
    text = path.read_text(encoding="utf-8")
    sender = next((l.split(":", 1)[1].strip() for l in text.splitlines() if l.lower().startswith("from:")), "")
    return {"found": True, "message_id": message_id, "from": sender, "text": text,
            "attachments": [], "extraction_schema": ORDER_SCHEMA}


def get_customer(email: str = "", name: str = "") -> dict:
    domain = email.split("@")[-1].lower() if email else ""
    for c in CUSTOMERS.values():
        if (domain and domain in c["email_domains"]) or (name and name.lower() in c["name"].lower()):
            return {"found": True, **{k: v for k, v in c.items() if k != "balance_owing"},
                    "available_credit": round(c["credit_limit"] - c["balance_owing"], 2)}
    return not_found("customer", email or name)


def get_price_list(customer_id: str, skus: list | None = None) -> dict:
    cust = CUSTOMERS.get(customer_id)
    if not cust:
        return not_found("customer", customer_id)
    pl = PRICE_LISTS[cust["price_list"]]
    items = pl["items"] if not skus else {s: pl["items"].get(s) for s in skus}
    return {"price_list": cust["price_list"], "currency": pl["currency"], "items": items}


def validate_order(customer_id: str, order: dict) -> dict:
    cust = CUSTOMERS.get(customer_id)
    if not cust:
        return not_found("customer", customer_id)
    errs = schema_errors(order, ORDER_SCHEMA)
    if errs:
        return {"valid_schema": False, "schema_errors": errs, "can_create_draft": False}
    result = check_order(order, cust, PRICE_LISTS[cust["price_list"]])
    return {"valid_schema": True, **result}


def flag_discrepancy(message_id: str, summary: str, discrepancies: list) -> dict:
    """Records discrepancies for the sales-ops queue and drafts nothing to the customer."""
    fid = f"FLAG-{uuid.uuid4().hex[:6].upper()}"
    STATE["flags"].append({"flag_id": fid, "message_id": message_id, "summary": summary,
                           "discrepancies": discrepancies})
    return {"flagged": True, "flag_id": fid}


def create_draft_order(customer_id: str, order: dict, discrepancy_notes: str = "") -> dict:
    """Requires human approval (runner-level gate). Creates a DRAFT, never a confirmed order."""
    check = validate_order(customer_id, order)
    if not check.get("can_create_draft"):
        return {"created": False, "error": "order has blocking discrepancies", "details": check}
    did = f"DRAFT-{uuid.uuid4().hex[:6].upper()}"
    STATE["drafts"].append({"draft_id": did, "customer_id": customer_id, "order": order,
                            "totals": check["totals"], "notes": discrepancy_notes})
    return {"created": True, "draft_id": did, "status": "draft", "totals": check["totals"]}


HANDLERS = {
    "get_po_document": get_po_document,
    "get_customer": get_customer,
    "get_price_list": get_price_list,
    "validate_order": validate_order,
    "flag_discrepancy": flag_discrepancy,
    "create_draft_order": create_draft_order,
}
