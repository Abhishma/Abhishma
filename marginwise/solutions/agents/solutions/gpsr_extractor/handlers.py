"""Mock handlers for the GPSR extractor.

TODO(adapters):
  - Supplier documents: Google Drive / SharePoint / email attachments; PDF text via
    pdfplumber, or Claude document blocks for scanned PDFs
  - Shopify Admin GraphQL: product(id) and metafieldsSet mutation (namespace "gpsr");
    metafield definitions should be created once per store with storefront access
"""

from __future__ import annotations

from pathlib import Path

from core.fixtures import load_json, not_found

from .gpsr import rule_based_extract, to_metafields, validate_fields

FIXTURES = Path(__file__).parent / "fixtures"
PRODUCTS = load_json(FIXTURES / "products.json")
STATE: dict[str, dict] = {"written": {}}


def reset_state() -> None:
    STATE["written"].clear()


def get_supplier_document(doc_id: str) -> dict:
    path = FIXTURES / "docs" / f"{doc_id}.txt"
    if not path.exists():
        return not_found("document", doc_id)
    text = path.read_text(encoding="utf-8")
    return {"found": True, "doc_id": doc_id, "text": text, "rule_based_fields": rule_based_extract(text)}


def get_product(product_id: str) -> dict:
    p = PRODUCTS.get(product_id)
    return {"found": True, **p} if p else not_found("product", product_id)


def validate_gpsr_fields(fields: dict, markets: list | None = None) -> dict:
    return validate_fields(fields, markets)


def write_metafields(product_id: str, fields: dict) -> dict:
    """Requires human approval (runner gate). Writes only non-empty fields."""
    if product_id not in PRODUCTS:
        return not_found("product", product_id)
    payload = to_metafields(product_id, fields)
    STATE["written"][product_id] = payload
    return {"written": True, "count": len(payload["metafields"]), "payload": payload}


HANDLERS = {
    "get_supplier_document": get_supplier_document,
    "get_product": get_product,
    "validate_gpsr_fields": validate_gpsr_fields,
    "write_metafields": write_metafields,
}
