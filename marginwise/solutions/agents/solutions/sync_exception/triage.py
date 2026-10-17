"""Deterministic first-pass classification of sync failures and safe fixes.

Rules catch the common error strings from Cin7, Unleashed, MYOB, Xero,
NetSuite, QuickBooks and DATEV connectors. Anything the rules cannot place
is labelled "unknown" and left to the LLM (cheap Haiku classification) or a
human. Only fixes in SAFE_FIXES may be auto-applied by retry_sync.
"""

from __future__ import annotations

import re

ROOT_CAUSES = [
    "missing_sku", "duplicate_order", "address_error", "tax_error",
    "inventory_mismatch", "payout_mismatch", "transient", "unknown",
]

_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("duplicate_order", re.compile(r"already exists|duplicate", re.I)),
    ("missing_sku", re.compile(r"(product|item|code|sku).{0,40}(not found|does not exist|unknown)", re.I)),
    ("inventory_mismatch", re.compile(r"insufficient stock|not enough stock|negative stock|available \d+, requested", re.I)),
    ("payout_mismatch", re.compile(r"payout.{0,40}(does not match|mismatch)", re.I)),
    ("tax_error", re.compile(r"\btax\b|steuerschl|gst|vat|mwst", re.I)),
    ("address_error", re.compile(r"country|postcode|postal|zip|state|province|address", re.I)),
    ("transient", re.compile(r"timeout|timed out|rate limit|429|503|temporarily", re.I)),
]

# Fix name -> human description. These are reversible and do not change money or stock.
SAFE_FIXES = {
    "trim_sku_whitespace": "Strip leading/trailing whitespace from line item SKUs",
    "normalize_country_code": "Convert ISO alpha-3 country (AUS) to alpha-2 (AU)",
    "round_tax_2dp": "Round line tax to 2 decimals (difference under 0.01)",
    "skip_duplicate": "Mark as synced because the ERP already holds this document",
    "retry_transient": "Plain retry after a timeout or rate-limit",
}

ALPHA3_TO_ALPHA2 = {"AUS": "AU", "NZL": "NZ", "USA": "US", "CAN": "CA", "DEU": "DE", "SAU": "SA", "GBR": "GB"}


def classify_failure(record: dict) -> str:
    err = record.get("error", "")
    for cause, pattern in _RULES:
        if pattern.search(err):
            return cause
    return "unknown"


def suggest_fix(record: dict, order: dict | None, erp_items: dict) -> dict:
    """Return {"cause", "fix", "safe", "detail"} for a failed sync record."""
    cause = classify_failure(record)
    fix, safe, detail = None, False, ""
    if cause == "missing_sku" and order:
        for li in order.get("line_items", []):
            sku = li["sku"]
            if sku not in erp_items and sku.strip() in erp_items:
                fix, safe, detail = "trim_sku_whitespace", True, f"'{sku}' -> '{sku.strip()}'"
                break
            if sku not in erp_items:
                close = _closest(sku, list(erp_items))
                fix, detail = "map_sku", f"Shopify SKU {sku} has no ERP item" + (f"; closest ERP code {close}" if close else "")
                break
    elif cause == "duplicate_order":
        fix, safe, detail = "skip_duplicate", True, "ERP already has the document; mark synced, do not create twice"
    elif cause == "address_error" and order and order.get("country") in ALPHA3_TO_ALPHA2:
        fix, safe, detail = "normalize_country_code", True, f"{order['country']} -> {ALPHA3_TO_ALPHA2[order['country']]}"
    elif cause == "tax_error":
        diff = _tax_rounding_diff(record.get("error", ""))
        if diff is not None and diff < 0.01:
            fix, safe, detail = "round_tax_2dp", True, f"rounding difference {diff:.4f}"
        else:
            detail = "Tax code or rate mismatch; needs accountant review (e.g. DATEV Steuerschluessel mapping)"
    elif cause == "inventory_mismatch":
        detail = "Stock at the requested location is short; transfer stock or change fulfilment location (human decision)"
    elif cause == "payout_mismatch":
        detail = "Payout total differs from invoices; usually fees, refunds or chargebacks not posted. Run payout reconciliation."
    elif cause == "transient":
        fix, safe, detail = "retry_transient", True, "Connector timeout; retry"
    return {"cause": cause, "fix": fix, "safe": safe, "detail": detail}


def _tax_rounding_diff(error: str) -> float | None:
    nums = re.findall(r"\d+\.\d+", error)
    if len(nums) >= 2:
        return abs(float(nums[0]) - float(nums[1]))
    return None


def _closest(sku: str, candidates: list[str]) -> str | None:
    """Very small similarity heuristic: shared prefix of at least 70% of the SKU."""
    best, best_len = None, 0
    for c in candidates:
        n = 0
        for a, b in zip(sku, c):
            if a != b:
                break
            n += 1
        if n > best_len:
            best, best_len = c, n
    return best if best_len >= 0.7 * len(sku) else None
