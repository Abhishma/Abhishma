"""Mock handlers for the Saudi WhatsApp commerce agent.

Data minimisation (PDPL): handlers return only the fields the agent needs for
the current step. Full phone numbers and full addresses are never returned to
the model; phone numbers are masked.

TODO(adapters):
  - Orders: Salla / Zid / Shopify Admin API
  - WhatsApp: Meta WhatsApp Cloud API (template messages for outbound COD confirmation)
  - Carriers: SMSA, Aramex, SPL, J&T, Naqel tracking APIs
  - National Address: SPL National Address API
  - Payments: Tabby / Tamara checkout session APIs for prepay links
"""

from __future__ import annotations

import uuid
from pathlib import Path

from core.fixtures import load_json, not_found, now, parse_dt

from .national_address import validate_short_address

FIXTURES = Path(__file__).parent / "fixtures"
DATA = load_json(FIXTURES / "orders.json")
STATE: dict[str, dict] = {"orders": {}, "returns": {}, "handoffs": {}}


def reset_state() -> None:
    for v in STATE.values():
        v.clear()


def _order(order_id: str) -> dict | None:
    if order_id in STATE["orders"]:
        return STATE["orders"][order_id]
    base = DATA["orders"].get(order_id)
    if base is None:
        return None
    STATE["orders"][order_id] = dict(base)
    return STATE["orders"][order_id]


def _mask_phone(phone: str) -> str:
    return phone[:4] + "*" * (len(phone) - 7) + phone[-3:]


def get_order(order_id: str = "", phone: str = "") -> dict:
    """Look up by order id, or by the WhatsApp sender phone (most recent order)."""
    order = _order(order_id) if order_id else None
    if order is None and phone:
        matches = [o for o in DATA["orders"].values() if o["phone"] == phone]
        if matches:
            order = _order(max(matches, key=lambda o: o["created_at"])["order_id"])
    if order is None:
        return not_found("order", order_id or "for this phone")
    return {
        "found": True,
        "order_id": order["order_id"],
        "first_name": order["customer_first_name"],
        "phone_masked": _mask_phone(order["phone"]),
        "status": order["status"],
        "payment_method": order["payment_method"],
        "total": order["total"],
        "currency": order["currency"],
        "items": [{"name": i["name"], "qty": i["qty"]} for i in order["items"]],
        "city": order["city"],
        "has_short_address": bool(order.get("short_address")),
        "fulfillment_status": order["fulfillment_status"],
        "prepay_link": order.get("prepay_link"),
        "prepay_incentive": DATA["store"]["prepay_incentive"] if order["payment_method"] == "cod" else None,
    }


def confirm_cod(order_id: str, confirmed: bool, reason: str = "") -> dict:
    order = _order(order_id)
    if order is None:
        return not_found("order", order_id)
    if order["payment_method"] != "cod":
        return {"updated": False, "error": "order is not cash on delivery"}
    if order["status"] != "pending_cod_confirmation":
        return {"updated": False, "error": f"order is already {order['status']}"}
    order["status"] = "confirmed" if confirmed else "cancelled_by_customer"
    if not confirmed:
        order["cancel_reason"] = reason
    return {"updated": True, "order_id": order_id, "status": order["status"]}


def validate_national_address(short_address: str) -> dict:
    # TODO(adapter): resolve with SPL National Address API after the format check.
    return validate_short_address(short_address)


def update_address(order_id: str, short_address: str, notes: str = "") -> dict:
    order = _order(order_id)
    if order is None:
        return not_found("order", order_id)
    if order["fulfillment_status"] != "unfulfilled":
        return {"updated": False, "error": "order already shipped; hand off to an agent to contact the carrier"}
    check = validate_short_address(short_address)
    if not check["valid"]:
        return {"updated": False, "error": "invalid short address", "details": check["errors"]}
    order["short_address"] = check["normalized"]
    order["address_notes"] = notes[:200]
    return {"updated": True, "order_id": order_id, "short_address": check["normalized"],
            "region_hint": check["region_hint"]}


def get_tracking(order_id: str) -> dict:
    order = _order(order_id)
    if order is None:
        return not_found("order", order_id)
    tn = order.get("tracking_number")
    if not tn:
        return {"order_id": order_id, "shipped": False, "status": order["status"],
                "message": "Not shipped yet. Orders usually ship within 1-2 business days of confirmation."}
    events = DATA["tracking"].get(tn, [])
    latest = events[-1] if events else None
    return {"order_id": order_id, "shipped": True, "carrier": order["carrier"],
            "tracking_number": tn, "latest": latest, "events": events[-3:],
            "needs_attention": bool(latest and "failed" in latest["status"])}


def create_return(order_id: str, skus: list, reason: str) -> dict:
    order = _order(order_id)
    if order is None:
        return not_found("order", order_id)
    if not order.get("delivered_at"):
        return {"created": False, "error": "order not delivered yet"}
    store = DATA["store"]
    age_days = (now() - parse_dt(order["delivered_at"])).days
    if age_days > store["return_window_days"]:
        return {"created": False, "error": f"outside {store['return_window_days']}-day return window ({age_days} days)"}
    accepted, rejected = [], []
    for sku in skus:
        item = next((i for i in order["items"] if i["sku"] == sku), None)
        if item is None:
            rejected.append({"sku": sku, "reason": "not in order"})
        elif item["category"] in store["non_returnable_categories"]:
            rejected.append({"sku": sku, "reason": "opened fragrance and personal care cannot be returned"})
        else:
            accepted.append(sku)
    if not accepted:
        return {"created": False, "rejected": rejected}
    rma = f"RMA-{uuid.uuid4().hex[:6].upper()}"
    STATE["returns"][rma] = {"order_id": order_id, "skus": accepted, "reason": reason}
    refund_to = "original payment method (Tabby/Tamara refunds adjust the instalment plan)" \
        if order["payment_method"] in ("tabby", "tamara") else "bank transfer or store credit"
    return {"created": True, "rma": rma, "accepted": accepted, "rejected": rejected,
            "pickup": "courier pickup booked within 2 business days", "refund_to": refund_to}


def handoff_to_agent(order_id: str = "", reason: str = "other", summary: str = "", language: str = "ar") -> dict:
    # TODO(adapter): assign the WhatsApp conversation to a human inbox (respond.io, Gorgias, Zendesk, Freshchat).
    hid = f"HO-{uuid.uuid4().hex[:6]}"
    STATE["handoffs"][hid] = {"order_id": order_id, "reason": reason, "summary": summary, "language": language}
    return {"handed_off": True, "handoff_id": hid, "support_hours": DATA["store"]["support_hours"],
            "ramadan_hours": DATA["store"]["ramadan_hours"]}


HANDLERS = {
    "get_order": get_order,
    "confirm_cod": confirm_cod,
    "update_address": update_address,
    "validate_national_address": validate_national_address,
    "get_tracking": get_tracking,
    "create_return": create_return,
    "handoff_to_agent": handoff_to_agent,
}
