"""Deterministic validation of an extracted purchase order.

1. schema_errors(): checks the extracted JSON against fixtures/order_schema.json
   (a small JSON-schema subset validator, no external dependency)
2. check_order(): business validation against the customer record and price
   list: unknown SKUs, price differences, MOQ and pack-size multiples, payment
   terms, ship-to, stated subtotal arithmetic, currency, credit limit.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

_TYPES = {"string": str, "number": (int, float), "integer": int, "boolean": bool,
          "array": list, "object": dict, "null": type(None)}


def schema_errors(value: Any, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    types = schema.get("type")
    if types:
        allowed = types if isinstance(types, list) else [types]
        ok = any(isinstance(value, _TYPES[t]) and not (t in ("number", "integer") and isinstance(value, bool))
                 for t in allowed)
        if not ok:
            return [f"{path}: expected {types}"]
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required")
        props = schema.get("properties", {})
        for key, sub in value.items():
            if key in props:
                errors += schema_errors(sub, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}.{key}: not allowed")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        for i, item in enumerate(value):
            errors += schema_errors(item, schema.get("items", {}), f"{path}[{i}]")
    return errors


def _money(x: float) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _norm(text: str) -> str:
    return " ".join((text or "").lower().replace(",", " ").split())


def check_order(order: dict, customer: dict, price_list: dict, price_tolerance_pct: float = 0.0) -> dict:
    """Return {"lines": [...priced lines...], "discrepancies": [...], "totals": {...}}.

    Each discrepancy: {"code", "severity" (block|review|info), "line_no", "detail"}.
    "block" means the draft order cannot be created until resolved.
    """
    issues: list[dict] = []

    def flag(code: str, severity: str, detail: str, line_no: int | None = None) -> None:
        issues.append({"code": code, "severity": severity, "line_no": line_no, "detail": detail})

    if order.get("currency") != price_list["currency"]:
        flag("currency_mismatch", "block", f"PO in {order.get('currency')}, price list in {price_list['currency']}")

    priced, subtotal = [], Decimal("0")
    for idx, line in enumerate(order.get("lines", []), start=1):
        ln = line.get("line_no", idx)
        item = price_list["items"].get(line["sku"])
        qty = Decimal(str(line["quantity"]))
        if item is None:
            flag("unknown_sku", "block", f"{line['sku']} ({line.get('description', '')}) is not on price list", ln)
            continue
        list_price = _money(item["unit_price"])
        po_price = _money(line["unit_price"])
        if list_price and abs(po_price - list_price) / list_price * 100 > Decimal(str(price_tolerance_pct)):
            flag("price_mismatch", "review",
                 f"{line['sku']}: PO price {po_price} vs list {list_price} (order will use list price unless approved)", ln)
        if qty < item.get("moq", 1):
            flag("below_moq", "review", f"{line['sku']}: qty {qty} below MOQ {item['moq']}", ln)
        pack = item.get("pack_size", 1)
        if pack > 1 and qty % pack != 0:
            flag("pack_multiple", "review", f"{line['sku']}: qty {qty} is not a multiple of pack size {pack}", ln)
        if line.get("uom") and line["uom"] != item["uom"]:
            flag("uom_mismatch", "review", f"{line['sku']}: PO unit {line['uom']} vs list {item['uom']}", ln)
        amount = _money(float(qty * list_price))
        subtotal += amount
        priced.append({"line_no": ln, "sku": line["sku"], "quantity": float(qty), "unit_price": float(list_price),
                       "po_unit_price": float(po_price), "amount": float(amount)})

    stated = order.get("stated_subtotal")
    if stated is not None:
        po_math = sum(_money(l["quantity"] * l["unit_price"]) for l in order.get("lines", []))
        if abs(_money(stated) - po_math) > Decimal("0.01"):
            flag("stated_subtotal_mismatch", "review",
                 f"PO states subtotal {_money(stated)} but its own lines add to {po_math}")

    if order.get("payment_terms") and _norm(order["payment_terms"]) != _norm(customer["payment_terms"]):
        flag("terms_mismatch", "review",
             f"PO terms '{order['payment_terms']}' differ from account terms '{customer['payment_terms']}'")

    ship = _norm(order.get("ship_to_address", ""))
    if ship and not any(_norm(s["address"]) in ship or ship in _norm(s["address"]) for s in customer["ship_to"]):
        flag("unknown_ship_to", "review", "ship-to address is not on the customer account")

    tax = (subtotal * Decimal(str(customer["tax"]["rate"]))).quantize(Decimal("0.01"))
    total = subtotal + tax
    headroom = Decimal(str(customer["credit_limit"])) - Decimal(str(customer["balance_owing"]))
    if total > headroom:
        flag("credit_limit", "review", f"order total {total} exceeds available credit {headroom}")

    blocking = any(i["severity"] == "block" for i in issues)
    return {
        "lines": priced,
        "discrepancies": issues,
        "totals": {"subtotal": float(subtotal), "tax": float(tax), "total": float(total),
                   "currency": price_list["currency"], "tax_name": customer["tax"]["name"]},
        "can_create_draft": not blocking,
    }
