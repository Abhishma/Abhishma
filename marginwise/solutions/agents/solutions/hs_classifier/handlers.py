"""Mock handlers for HS code suggestion and landed cost.

TODO(adapters):
  - Product data: Shopify Admin API (product, variants, metafields: material, origin)
  - Nomenclature / national lines: USITC HTS REST API (hts.usitc.gov), CBSA Customs
    Tariff, WCO HS database licence, or a classification provider (Zonos, Avalara,
    Descartes) for rate lookups
  - Review queue: Airtable / Sheets / Linear issue per SKU; on approval write
    harmonized_system_code and country_code_of_origin to the Shopify inventory item
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from core.fixtures import load_json, not_found

from .landed_cost import calculate_landed_cost as _calc

FIXTURES = Path(__file__).parent / "fixtures"
NOMENCLATURE = load_json(FIXTURES / "hs_nomenclature.json")["subheadings"]
PRODUCTS = load_json(FIXTURES / "products.json")
STATE: dict[str, list] = {"reviews": []}


def reset_state() -> None:
    STATE["reviews"].clear()


def get_product(sku: str) -> dict:
    p = PRODUCTS.get(sku)
    return {"found": True, **p} if p else not_found("product", sku)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9\-]+", text.lower()))


def search_hs_nomenclature(query: str, limit: int = 5) -> dict:
    """Keyword-overlap search over the offline subset (real adapter: HTS / WCO search)."""
    q = query.lower()
    qt = _tokens(q)
    scored = []
    for h in NOMENCLATURE:
        score = 0
        for kw in h["keywords"]:
            if " " in kw or "-" in kw:
                score += 3 if kw in q else 0
            elif kw in qt:
                score += 2
        score += len(qt & _tokens(h["description"]))
        if score:
            scored.append((score, h))
    scored.sort(key=lambda x: -x[0])
    return {"query": query, "results": [{"code": h["code"], "description": h["description"], "score": s}
                                        for s, h in scored[:limit]],
            "note": "Offline subset only; confirm against the full HS / national tariff."}


def calculate_landed_cost(goods_value: float, fx_rate: float, duty_rate_pct: float, destination: str,
                          tariff_surcharge_pct: float = 0, freight: float = 0, insurance: float = 0,
                          quantity: int = 1, mode: str = "air", import_tax_pct: float | None = None,
                          broker_fee: float = 0) -> dict:
    return _calc(goods_value=goods_value, fx_rate=fx_rate, duty_rate_pct=duty_rate_pct,
                 destination=destination, tariff_surcharge_pct=tariff_surcharge_pct, freight=freight,
                 insurance=insurance, quantity=quantity, mode=mode, import_tax_pct=import_tax_pct,
                 broker_fee=broker_fee)


def submit_for_review(sku: str, suggestions: list, rationale: str, destination_markets: list,
                      open_questions: list | None = None) -> dict:
    """Every classification goes to a licensed broker / trade specialist. Nothing is applied."""
    if not suggestions:
        return {"submitted": False, "error": "at least one suggestion required"}
    for s in suggestions:
        if not re.fullmatch(r"\d{4}\.\d{2}", str(s.get("hs6", ""))):
            return {"submitted": False, "error": f"hs6 must look like 6109.10, got {s.get('hs6')}"}
        if not 0 <= float(s.get("confidence", -1)) <= 1:
            return {"submitted": False, "error": "confidence must be between 0 and 1"}
    rid = f"HSR-{uuid.uuid4().hex[:6].upper()}"
    STATE["reviews"].append({"review_id": rid, "sku": sku, "suggestions": suggestions, "rationale": rationale,
                             "markets": destination_markets, "open_questions": open_questions or []})
    return {"submitted": True, "review_id": rid, "status": "awaiting_human_review"}


HANDLERS = {
    "get_product": get_product,
    "search_hs_nomenclature": search_hs_nomenclature,
    "calculate_landed_cost": calculate_landed_cost,
    "submit_for_review": submit_for_review,
}
