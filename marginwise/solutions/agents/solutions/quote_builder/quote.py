"""Deterministic quote calculation and quote document building for trades.

Prices in the price book are ex tax with a low/high range per unit. A quote
line is the range times quantity, with an optional minimum charge. Taxes are
applied per business config (AU GST 10%, NZ GST 15%, DE USt 19%, US/CA as
configured). Items flagged requires_site_visit can only be estimated.

German "Angebot": a binding offer, so every line needs a fixed price
(low == high). Mandatory fields of our Angebot template are validated in
validate_angebot(). Range prices must go out as an "unverbindliche
Kostenschaetzung" (estimate) and be firmed up after a site visit.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _q(x) -> Decimal:
    return Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP)


def calculate(price_book: dict, items: list[dict], tax: dict) -> dict:
    """items: [{"item_id", "quantity", "answers": {...}}]. Returns ranged totals."""
    lines, errors, missing_answers, site_visit = [], [], [], False
    sub_low = sub_high = Decimal("0")
    for it in items:
        entry = price_book.get(it["item_id"])
        if entry is None:
            errors.append(f"unknown item {it['item_id']}")
            continue
        qty = Decimal(str(it.get("quantity", 1)))
        if qty <= 0:
            errors.append(f"quantity for {it['item_id']} must be positive")
            continue
        answers = it.get("answers", {}) or {}
        gaps = [q for q in entry.get("questions", []) if q not in answers]
        if gaps:
            missing_answers.append({"item_id": it["item_id"], "questions": gaps})
        low, high = _q(Decimal(str(entry["low"])) * qty), _q(Decimal(str(entry["high"])) * qty)
        min_charge = entry.get("min_charge")
        if min_charge is not None:
            low, high = max(low, _q(min_charge)), max(high, _q(min_charge))
        site_visit = site_visit or entry.get("requires_site_visit", False)
        sub_low += low
        sub_high += high
        lines.append({"item_id": it["item_id"], "label": entry["label"], "unit": entry["unit"],
                      "quantity": float(qty), "unit_low": float(entry["low"]), "unit_high": float(entry["high"]),
                      "low": float(low), "high": float(high), "fixed_price": entry["low"] == entry["high"],
                      "requires_site_visit": entry.get("requires_site_visit", False)})
    rate = Decimal(str(tax["rate_pct"])) / 100
    tax_low, tax_high = _q(sub_low * rate), _q(sub_high * rate)
    return {
        "lines": lines,
        "errors": errors,
        "missing_answers": missing_answers,
        "requires_site_visit": site_visit,
        "subtotal_low": float(sub_low), "subtotal_high": float(sub_high),
        "tax_name": tax["name"], "tax_rate_pct": tax["rate_pct"],
        "tax_low": float(tax_low), "tax_high": float(tax_high),
        "total_low": float(sub_low + tax_low), "total_high": float(sub_high + tax_high),
        "is_fixed": all(l["fixed_price"] for l in lines) and bool(lines),
    }


ANGEBOT_REQUIRED = [
    "angebotsnummer", "datum", "gueltig_bis",
    "anbieter.name", "anbieter.anschrift", "anbieter.steuer_id",
    "kunde.name", "kunde.anschrift",
    "positionen", "netto_summe", "ust_satz", "ust_betrag", "brutto_summe", "zahlungsbedingungen",
]


def _get(doc: dict, dotted: str):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def validate_angebot(doc: dict) -> list[str]:
    """Return a list of problems; empty means the Angebot meets our template rules."""
    problems = [f"Pflichtfeld fehlt: {f}" for f in ANGEBOT_REQUIRED if _get(doc, f) in (None, "", [])]
    for i, p in enumerate(doc.get("positionen") or [], start=1):
        for f in ("beschreibung", "menge", "einheit", "einzelpreis_netto", "gesamt_netto"):
            if p.get(f) in (None, ""):
                problems.append(f"Position {i}: {f} fehlt")
    if doc.get("netto_summe") is not None and doc.get("positionen"):
        s = sum(_q(p.get("gesamt_netto", 0)) for p in doc["positionen"])
        if s != _q(doc["netto_summe"]):
            problems.append(f"netto_summe {doc['netto_summe']} != Summe der Positionen {s}")
    if None not in (doc.get("netto_summe"), doc.get("ust_betrag"), doc.get("brutto_summe")):
        if _q(doc["netto_summe"]) + _q(doc["ust_betrag"]) != _q(doc["brutto_summe"]):
            problems.append("brutto_summe != netto_summe + ust_betrag")
    return problems


def build_document(business: dict, quote: dict, customer: dict, doc_type: str, number: str,
                   issue_date: date) -> dict:
    """Build a PDF-ready JSON document (estimate in any market, Angebot for DE)."""
    valid_until = issue_date + timedelta(days=business.get("quote_validity_days", 30))
    if doc_type == "angebot":
        if not quote["is_fixed"]:
            return {"ok": False, "error": "Angebot requires fixed prices for every line; send an estimate "
                                          "(unverbindliche Kostenschaetzung) and book a site visit"}
        rate = Decimal(str(quote["tax_rate_pct"]))
        positions = [{"pos": i, "beschreibung": l["label"], "menge": l["quantity"], "einheit": l["unit"],
                      "einzelpreis_netto": l["unit_low"], "gesamt_netto": l["low"]}
                     for i, l in enumerate(quote["lines"], start=1)]
        netto = _q(sum(Decimal(str(p["gesamt_netto"])) for p in positions))
        ust = _q(netto * rate / 100)
        doc = {
            "doc_type": "angebot", "angebotsnummer": number, "datum": issue_date.strftime("%d.%m.%Y"),
            "gueltig_bis": valid_until.strftime("%d.%m.%Y"),
            "anbieter": {"name": business["name"], "anschrift": business["address"],
                         "steuer_id": business.get("ust_id") or business.get("steuernummer"),
                         "hinweis": business.get("handwerksrolle", "")},
            "kunde": {"name": customer.get("name"), "anschrift": customer.get("address")},
            "positionen": positions, "netto_summe": float(netto), "ust_satz": float(rate),
            "ust_betrag": float(ust), "brutto_summe": float(netto + ust), "waehrung": "EUR",
            "zahlungsbedingungen": customer.get("payment_terms") or "Zahlbar innerhalb von 14 Tagen nach Rechnungsstellung ohne Abzug.",
            "hinweise": ["Kleinunternehmer gemaess § 19 UStG, keine Umsatzsteuer ausgewiesen."] if business.get("kleinunternehmer") else [],
        }
        problems = validate_angebot(doc)
        return {"ok": not problems, "document": doc, "problems": problems}

    doc = {
        "doc_type": "estimate", "number": number, "date": issue_date.isoformat(), "valid_until": valid_until.isoformat(),
        "business": {"name": business["name"], "address": business["address"],
                     "abn": business.get("abn"), "licence": business.get("licence")},
        "customer": {"name": customer.get("name"), "address": customer.get("address")},
        "currency": business["currency"],
        "lines": [{"description": l["label"], "quantity": l["quantity"], "unit": l["unit"],
                   "range": [l["low"], l["high"]]} for l in quote["lines"]],
        "subtotal_range": [quote["subtotal_low"], quote["subtotal_high"]],
        "tax": {"name": quote["tax_name"], "rate_pct": quote["tax_rate_pct"], "range": [quote["tax_low"], quote["tax_high"]]},
        "total_range": [quote["total_low"], quote["total_high"]],
        "terms": ["Estimate only; final price confirmed in writing after inspection.",
                  "Prices assume standard access and no hidden damage."],
        "site_visit_required": quote["requires_site_visit"],
    }
    if doc["customer"]["name"] in (None, ""):
        return {"ok": False, "error": "customer name required"}
    return {"ok": True, "document": doc, "problems": []}
