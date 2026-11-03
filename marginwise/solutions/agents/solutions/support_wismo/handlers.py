"""Mock handlers for the ecommerce support (WISMO / returns / exchanges) agent.

TODO(adapters):
  - Shopify Admin GraphQL: orders(query: "name:#1042"), orderEditBegin/Commit, returnCreate
  - Tracking: AfterShip / Shippo / carrier APIs (UPS, USPS, FedEx, Canada Post, AusPost)
  - Returns platform (optional): Loop, Redo, AfterShip Returns
  - Helpdesk: Gorgias tickets/{id}/messages (internal note), Zendesk tickets/{id} comments public=false
"""

from __future__ import annotations

import uuid
from pathlib import Path

from core.fixtures import load_json, not_found, now, parse_dt

FIXTURES = Path(__file__).parent / "fixtures"
SHOP = load_json(FIXTURES / "shop.json")
STATE: dict[str, list] = {"returns": [], "exchanges": [], "notes": [], "escalations": [], "address_edits": []}


def reset_state() -> None:
    for v in STATE.values():
        v.clear()


def _find(order_number: str) -> dict | None:
    key = order_number if order_number.startswith("#") else f"#{order_number}"
    return SHOP["orders"].get(key)


def lookup_order(order_number: str, email: str) -> dict:
    """Identity check: order number AND email must match before details are shared."""
    order = _find(order_number)
    if order is None or order["email"].lower() != email.strip().lower():
        return {"found": False, "error": "no order matches that order number and email"}
    return {
        "found": True,
        "order_number": order["name"],
        "created_at": order["created_at"],
        "financial_status": order["financial_status"],
        "fulfillment_status": order["fulfillment_status"] or "unfulfilled",
        "ship_to_city": order["shipping_address"]["city"],
        "ship_to_country": order["shipping_address"]["country_code"],
        "line_items": [{"id": li["id"], "title": li["title"], "sku": li["sku"], "quantity": li["quantity"],
                        "final_sale": bool(set(li["tags"]) & set(SHOP["policy"]["final_sale_tags"]))}
                       for li in order["line_items"]],
        "delivered_at": order.get("delivered_at"),
    }


def get_tracking(order_number: str) -> dict:
    order = _find(order_number)
    if order is None:
        return not_found("order", order_number)
    tn = order.get("tracking_number")
    if not tn:
        return {"shipped": False, "message": "Not shipped yet; most orders ship within 2 business days."}
    return {"shipped": True, "carrier": order["carrier"], "tracking_number": tn, **SHOP["tracking"].get(tn, {})}


def _days_since_delivery(order: dict) -> int | None:
    if not order.get("delivered_at"):
        return None
    return (now() - parse_dt(order["delivered_at"])).days


def start_return(order_number: str, line_item_ids: list, reason: str) -> dict:
    order = _find(order_number)
    if order is None:
        return not_found("order", order_number)
    policy = SHOP["policy"]
    days = _days_since_delivery(order)
    if days is None:
        return {"created": False, "error": "order not delivered yet; offer cancellation via escalate if unfulfilled"}
    if days > policy["return_window_days"]:
        return {"created": False, "error": f"outside {policy['return_window_days']}-day return window ({days} days since delivery)"}
    accepted, rejected = [], []
    for lid in line_item_ids:
        li = next((x for x in order["line_items"] if x["id"] == lid), None)
        if li is None:
            rejected.append({"line_item_id": lid, "reason": "not on order"})
        elif set(li["tags"]) & set(policy["final_sale_tags"]):
            rejected.append({"line_item_id": lid, "reason": "final sale"})
        else:
            accepted.append(lid)
    if not accepted:
        return {"created": False, "rejected": rejected}
    fee = 0.0 if reason in policy["free_return_reasons"] else policy["return_label_fee"]
    rid = f"RET-{uuid.uuid4().hex[:6].upper()}"
    STATE["returns"].append({"return_id": rid, "order": order["name"], "items": accepted, "reason": reason})
    return {"created": True, "return_id": rid, "accepted": accepted, "rejected": rejected,
            "label_fee": fee, "currency": policy["currency"],
            "label": "prepaid label emailed to the address on the order"}


def offer_exchange(order_number: str, line_item_id: str, new_sku: str) -> dict:
    order = _find(order_number)
    if order is None:
        return not_found("order", order_number)
    days = _days_since_delivery(order)
    if days is not None and days > SHOP["policy"]["exchange_window_days"]:
        return {"available": False, "error": "outside exchange window"}
    li = next((x for x in order["line_items"] if x["id"] == line_item_id), None)
    if li is None:
        return {"available": False, "error": "line item not on order"}
    stock = SHOP["inventory"].get(new_sku)
    if stock is None:
        return {"available": False, "error": f"unknown sku {new_sku}"}
    if stock <= 0:
        return {"available": False, "error": f"{new_sku} out of stock", "suggest": "offer return or a different size"}
    xid = f"EXC-{uuid.uuid4().hex[:6].upper()}"
    STATE["exchanges"].append({"exchange_id": xid, "order": order["name"], "from": li["sku"], "to": new_sku})
    return {"available": True, "exchange_id": xid, "ships": "when the original item is scanned by the carrier",
            "price_difference": 0.0}


def edit_order_address(order_number: str, address1: str, city: str, province_code: str,
                       zip: str, country_code: str, address2: str = "") -> dict:
    """Requires human approval (enforced by the runner via tools.json)."""
    order = _find(order_number)
    if order is None:
        return not_found("order", order_number)
    if order["fulfillment_status"]:
        return {"updated": False, "error": "order already fulfilled; address can no longer be edited"}
    if country_code != order["shipping_address"]["country_code"]:
        return {"updated": False, "error": "cross-border address changes need a new order"}
    new = {"address1": address1, "address2": address2, "city": city,
           "province_code": province_code, "zip": zip, "country_code": country_code}
    STATE["address_edits"].append({"order": order["name"], "new": new})
    return {"updated": True, "order_number": order["name"]}


def add_ticket_note(ticket_id: str, note: str) -> dict:
    STATE["notes"].append({"ticket_id": ticket_id, "note": note})
    return {"added": True, "ticket_id": ticket_id, "visibility": "internal"}


def escalate(ticket_id: str, reason: str, priority: str = "normal", summary: str = "") -> dict:
    STATE["escalations"].append({"ticket_id": ticket_id, "reason": reason, "priority": priority, "summary": summary})
    return {"escalated": True, "ticket_id": ticket_id, "queue": "tier2" if priority != "urgent" else "lead"}


HANDLERS = {
    "lookup_order": lookup_order,
    "get_tracking": get_tracking,
    "start_return": start_return,
    "offer_exchange": offer_exchange,
    "edit_order_address": edit_order_address,
    "add_ticket_note": add_ticket_note,
    "escalate": escalate,
}
