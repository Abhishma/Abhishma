"""Mock handlers for the trades quote builder.

TODO(adapters):
  - Price book: client's spreadsheet / ServiceM8 or simPRO price lists / Jobber products
  - Quotes: ServiceM8 quote job, simPRO quotes, Tradify quotes, Jobber quotes,
    Housecall Pro estimates; German Angebot via lexoffice / sevDesk / Billomat API
  - PDF rendering: the JSON document is rendered by a template (WeasyPrint, DocRaptor)
  - Site visits: the same calendars as the receptionist solution
"""

from __future__ import annotations

import uuid
from pathlib import Path

from core.fixtures import load_json, not_found, now

from .quote import build_document, calculate

FIXTURES = Path(__file__).parent / "fixtures"
BUSINESSES = load_json(FIXTURES / "businesses.json")
PRICE_BOOK = load_json(FIXTURES / "price_book.json")
STATE: dict = {"quotes": {}, "documents": {}, "visits": [], "transfers": []}


def reset_state() -> None:
    for v in STATE.values():
        v.clear()


def get_price_book(business_id: str, trade: str = "") -> dict:
    book = PRICE_BOOK.get(business_id)
    if book is None:
        return not_found("business", business_id)
    items = {k: v for k, v in book.items() if not trade or v["trade"] == trade}
    biz = BUSINESSES[business_id]
    return {"business": biz["name"], "market": biz["market"], "currency": biz["currency"],
            "tax": biz["tax"], "items": items}


def calculate_quote(business_id: str, items: list) -> dict:
    biz = BUSINESSES.get(business_id)
    if biz is None:
        return not_found("business", business_id)
    result = calculate(PRICE_BOOK[business_id], items, biz["tax"])
    if result["errors"]:
        return {"ok": False, **result}
    qid = f"Q-{uuid.uuid4().hex[:6].upper()}"
    STATE["quotes"][qid] = result
    return {"ok": True, "quote_id": qid, "currency": biz["currency"], **result}


def create_quote_document(business_id: str, quote_id: str, customer_name: str, customer_address: str,
                          doc_type: str = "estimate", payment_terms: str = "") -> dict:
    biz = BUSINESSES.get(business_id)
    quote = STATE["quotes"].get(quote_id)
    if biz is None or quote is None:
        return not_found("business or quote", f"{business_id}/{quote_id}")
    if doc_type == "angebot" and biz["market"] != "DE":
        return {"ok": False, "error": "Angebot format is for German businesses only"}
    number = f"{'AN' if doc_type == 'angebot' else 'EST'}-{now().year}-{len(STATE['documents']) + 1:04d}"
    out = build_document(biz, quote, {"name": customer_name, "address": customer_address,
                                      "payment_terms": payment_terms}, doc_type, number, now().date())
    if out.get("ok"):
        STATE["documents"][number] = out["document"]
    return out


def check_site_visit_slots(business_id: str) -> dict:
    biz = BUSINESSES.get(business_id)
    if biz is None:
        return not_found("business", business_id)
    taken = {v["slot_id"] for v in STATE["visits"]}
    return {"slots": [s for s in biz["slots"] if s["slot_id"] not in taken]}


def book_site_visit(business_id: str, slot_id: str, customer_name: str, phone: str, address: str,
                    quote_id: str = "") -> dict:
    biz = BUSINESSES.get(business_id)
    if biz is None:
        return not_found("business", business_id)
    slot = next((s for s in biz["slots"] if s["slot_id"] == slot_id), None)
    if slot is None or any(v["slot_id"] == slot_id for v in STATE["visits"]):
        return {"booked": False, "error": "slot unavailable; call check_site_visit_slots"}
    vid = f"SV-{uuid.uuid4().hex[:6].upper()}"
    STATE["visits"].append({"visit_id": vid, "slot_id": slot_id, "customer_name": customer_name,
                            "phone": phone, "address": address, "quote_id": quote_id})
    return {"booked": True, "visit_id": vid, "start": slot["start"]}


def transfer_to_human(business_id: str, reason: str, summary: str = "") -> dict:
    STATE["transfers"].append({"business_id": business_id, "reason": reason, "summary": summary})
    return {"transferred": True, "reason": reason}


HANDLERS = {
    "get_price_book": get_price_book,
    "calculate_quote": calculate_quote,
    "create_quote_document": create_quote_document,
    "check_site_visit_slots": check_site_visit_slots,
    "book_site_visit": book_site_visit,
    "transfer_to_human": transfer_to_human,
}
