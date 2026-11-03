"""Mock handlers for Shopify-to-ERP sync exception triage.

TODO(adapters):
  - Failed sync source: connector logs / middleware (Cin7 Core integration log, Unleashed
    sync queue, Xero/MYOB connector such as A2X/Link My Books, NetSuite Celigo errors,
    QuickBooks connector, DATEV export validation)
  - Shopify Admin GraphQL order(id) for order detail
  - ERP item lookup: Cin7 /Product, Unleashed /Products, NetSuite inventoryItem search,
    Xero /Items, MYOB /Inventory/Item, QuickBooks /item
  - Slack chat.postMessage (bot token, channel id)
"""

from __future__ import annotations

import copy
from pathlib import Path

from core.fixtures import load_json, not_found
from core.guardrails import pending_approval

from .triage import SAFE_FIXES, suggest_fix

FIXTURES = Path(__file__).parent / "fixtures"
DATA = load_json(FIXTURES / "data.json")
STATE: dict = {"syncs": {}, "mappings": {}, "slack": [], "retries": []}


def reset_state() -> None:
    STATE["syncs"] = {r["sync_id"]: copy.deepcopy(r) for r in DATA["failed_syncs"]}
    STATE["mappings"] = {}
    STATE["slack"] = []
    STATE["retries"] = []


reset_state()


def list_failed_syncs(erp: str = "", limit: int = 50) -> dict:
    out = []
    for rec in STATE["syncs"].values():
        if rec.get("status") == "resolved":
            continue
        if erp and rec["erp"].lower() != erp.lower():
            continue
        order = DATA["shopify_orders"].get(rec.get("shopify_order") or "")
        out.append({**rec, "triage": suggest_fix(rec, order, DATA["erp_items"])})
    return {"count": len(out[:limit]), "records": out[:limit], "safe_fixes": SAFE_FIXES}


def get_shopify_order(order_name: str) -> dict:
    order = DATA["shopify_orders"].get(order_name)
    return {"found": True, **order} if order else not_found("order", order_name)


def get_erp_item(sku: str) -> dict:
    code = STATE["mappings"].get(sku, sku)
    item = DATA["erp_items"].get(code)
    return {"found": True, **item} if item else not_found("ERP item", sku)


def map_sku(shopify_sku: str, erp_code: str) -> dict:
    """Creates a SKU mapping. Gated by the runner (requires_approval)."""
    if erp_code not in DATA["erp_items"]:
        return {"mapped": False, "error": f"ERP code {erp_code} does not exist"}
    STATE["mappings"][shopify_sku] = erp_code
    return {"mapped": True, "shopify_sku": shopify_sku, "erp_code": erp_code}


def retry_sync(sync_id: str, fix: str = "", approved: bool = False) -> dict:
    """Retry a sync, optionally applying a fix. Non-whitelisted fixes need approval."""
    rec = STATE["syncs"].get(sync_id)
    if rec is None:
        return not_found("sync", sync_id)
    if fix and fix not in SAFE_FIXES and not approved:
        return pending_approval("retry_sync", {"sync_id": sync_id, "fix": fix},
                                reason=f"fix '{fix}' is not on the auto-apply whitelist")
    order = DATA["shopify_orders"].get(rec.get("shopify_order") or "")
    triage = suggest_fix(rec, order, DATA["erp_items"])
    # A mapped SKU resolves a missing_sku failure.
    if triage["cause"] == "missing_sku" and order and all(
        li["sku"] in STATE["mappings"] or li["sku"] in DATA["erp_items"] or
        (fix == "trim_sku_whitespace" and li["sku"].strip() in DATA["erp_items"])
        for li in order["line_items"]
    ):
        ok = True
    elif fix and fix == triage["fix"]:
        ok = True
    elif fix and approved:
        ok = True
    else:
        ok = False
    rec["attempts"] = rec.get("attempts", 0) + 1
    STATE["retries"].append({"sync_id": sync_id, "fix": fix, "ok": ok})
    if ok:
        rec["status"] = "resolved"
        return {"retried": True, "success": True, "sync_id": sync_id, "fix_applied": fix or None}
    return {"retried": True, "success": False, "sync_id": sync_id,
            "error": rec["error"], "hint": triage["detail"]}


def post_slack(channel: str, text: str) -> dict:
    if len(text) > 3500:
        return {"posted": False, "error": "message too long; summarise (max 3500 chars)"}
    STATE["slack"].append({"channel": channel, "text": text})
    return {"posted": True, "channel": channel, "ts": f"{len(STATE['slack'])}.000100"}


HANDLERS = {
    "list_failed_syncs": list_failed_syncs,
    "get_shopify_order": get_shopify_order,
    "get_erp_item": get_erp_item,
    "map_sku": map_sku,
    "retry_sync": retry_sync,
    "post_slack": post_slack,
}
