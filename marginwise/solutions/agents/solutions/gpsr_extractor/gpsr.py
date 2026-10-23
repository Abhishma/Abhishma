"""EU GPSR (Regulation (EU) 2023/988) field handling: rule-based extraction,
validation and Shopify metafield output.

Required for products sold online to EU consumers (Art. 19, online offers):
  - manufacturer name, postal address and electronic address (email or URL)
  - if the manufacturer is outside the EU: the EU responsible person
    (name, postal address, electronic address)
  - product identifier (type, batch or serial number) and a picture/type info
  - warnings or safety information, in the language(s) of the target market

The rule-based extractor handles labelled supplier sheets (English and German
labels). The LLM handles free-form documents; both feed validate_fields().
"""

from __future__ import annotations

import json
import re

EU_EEA_COUNTRIES = {
    "austria", "belgium", "bulgaria", "croatia", "cyprus", "czechia", "czech republic", "denmark",
    "estonia", "finland", "france", "germany", "deutschland", "greece", "hungary", "ireland", "italy",
    "latvia", "lithuania", "luxembourg", "malta", "netherlands", "poland", "portugal", "romania",
    "slovakia", "slovenia", "spain", "sweden", "österreich", "oesterreich", "frankreich", "niederlande",
    "iceland", "liechtenstein", "norway",
}

FIELDS = [
    "manufacturer_name", "manufacturer_address", "manufacturer_email",
    "eu_rp_name", "eu_rp_address", "eu_rp_email",
    "product_identifier", "warnings",
]

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URL = re.compile(r"https?://\S+")

_LABELS = {
    "manufacturer_name": r"(manufacturer|hersteller|made by)",
    "manufacturer_address": r"(address|adresse|anschrift)",
    "manufacturer_email": r"(e-?mail|contact email)",
    "eu_rp": r"(eu responsible person|eu-verantwortliche[rn]? person|verantwortliche person in der eu|eu rep(resentative)?)",
    "type": r"(model\s*/\s*type|model|type|typ|modell|art\.?-?nr\.?)",
    "batch": r"(batch|lot|charge|serial( number)?|seriennummer)",
    "warnings": r"(warnings?|warnhinweise?|safety information|sicherheitshinweise)",
}


def _line_value(text: str, label_regex: str) -> str | None:
    m = re.search(rf"^\s*{label_regex}\s*:\s*(.+)$", text, re.I | re.M)
    return m.group(m.lastindex).strip() if m else None


def _country_in(address: str) -> str | None:
    tail = address.split(",")[-1].strip().lower()
    return tail or None


def rule_based_extract(text: str) -> dict:
    """Extract labelled GPSR fields. Missing values are None."""
    out: dict = {f: None for f in FIELDS}
    out["manufacturer_name"] = _line_value(text, _LABELS["manufacturer_name"])
    out["manufacturer_address"] = _line_value(text, _LABELS["manufacturer_address"])
    out["manufacturer_email"] = _line_value(text, _LABELS["manufacturer_email"])
    rp = _line_value(text, _LABELS["eu_rp"])
    if rp:
        email = _EMAIL.search(rp)
        rp_wo_email = _EMAIL.sub("", rp).strip(" ,;")
        parts = [p.strip() for p in rp_wo_email.split(",") if p.strip()]
        out["eu_rp_name"] = parts[0] if parts else None
        out["eu_rp_address"] = ", ".join(parts[1:]) or None
        out["eu_rp_email"] = email.group(0) if email else None
    ptype, batch = _line_value(text, _LABELS["type"]), _line_value(text, _LABELS["batch"])
    ident = "; ".join(x for x in [f"Type {ptype}" if ptype else None, f"Batch {batch}" if batch else None] if x)
    out["product_identifier"] = ident or None
    out["warnings"] = _line_value(text, _LABELS["warnings"])
    return out


def validate_fields(fields: dict, markets: list[str] | None = None) -> dict:
    """Return {"complete", "missing", "problems"} for a GPSR field set."""
    missing, problems = [], []
    for f in ("manufacturer_name", "manufacturer_address", "product_identifier", "warnings"):
        if not fields.get(f):
            missing.append(f)
    m_contact = fields.get("manufacturer_email") or ""
    if not m_contact:
        missing.append("manufacturer_email")
    elif not (_EMAIL.fullmatch(m_contact.strip()) or _URL.match(m_contact.strip())):
        problems.append("manufacturer_email is not a valid email address or URL")

    m_country = _country_in(fields.get("manufacturer_address") or "")
    manufacturer_in_eu = bool(m_country and m_country in EU_EEA_COUNTRIES)
    if not manufacturer_in_eu:
        for f in ("eu_rp_name", "eu_rp_address", "eu_rp_email"):
            if not fields.get(f):
                missing.append(f)
        rp_country = _country_in(fields.get("eu_rp_address") or "")
        if fields.get("eu_rp_address") and rp_country not in EU_EEA_COUNTRIES:
            problems.append(f"EU responsible person address country '{rp_country}' is not in the EU/EEA")
        if fields.get("eu_rp_email") and not _EMAIL.fullmatch(fields["eu_rp_email"].strip()):
            problems.append("eu_rp_email is not a valid email address")

    if markets and fields.get("warnings") and "DE" in [m.upper() for m in markets]:
        if not re.search(r"\b(nicht|achtung|warnung|vorsicht|geeignet|kinder)\b", fields["warnings"], re.I):
            problems.append("warnings appear to have no German text for the DE market")

    return {"complete": not missing and not problems, "missing": missing, "problems": problems,
            "manufacturer_in_eu": manufacturer_in_eu}


def to_metafields(product_id: str, fields: dict, namespace: str = "gpsr") -> dict:
    """Shopify metafieldsSet input (single_line_text_field / multi_line_text_field)."""
    multi = {"manufacturer_address", "eu_rp_address", "warnings"}
    metafields = []
    for key in FIELDS:
        value = fields.get(key)
        if not value:
            continue
        metafields.append({
            "ownerId": product_id, "namespace": namespace, "key": key,
            "type": "multi_line_text_field" if key in multi else "single_line_text_field",
            "value": str(value),
        })
    return {"metafields": metafields}


def dumps(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)
