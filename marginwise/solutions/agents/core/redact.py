"""PII redaction for logs and transcripts.

Redaction is applied to what we WRITE TO DISK, never to what the model or the
tool handlers see. The goal is that a transcript can be shared with the client
or attached to a ticket without leaking customer contact or payment data.

Patterns are intentionally conservative (prefer over-redaction in logs).
"""

from __future__ import annotations

import re
from typing import Any

# Order matters: card numbers before generic phone numbers.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    # IBAN (DE, SA and others): 2 letters, 2 digits, 11-30 alphanumerics, optional spaces.
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,4})?\b")),
    # Payment card numbers: 13-19 digits with optional spaces or dashes.
    ("CARD", re.compile(r"\b(?:\d[ -]?){12,18}\d\b")),
    # Phone numbers: international or local formats with at least 8 digits.
    ("PHONE", re.compile(r"(?<![\w])(?:\+|00)?\d[\d ()\-]{6,}\d(?![\w])")),
]

# Dictionary keys whose values are always masked, regardless of content.
SENSITIVE_KEYS = {
    "phone", "mobile", "email", "customer_email", "customer_phone", "to",
    "card_number", "iban", "national_id", "iqama", "date_of_birth", "dob",
    "tax_file_number", "sin", "ssn", "password", "api_key",
}


_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def _luhn_ok(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def _replace(label: str, match: re.Match[str]) -> str:
    raw = match.group(0)
    digits = re.sub(r"\D", "", raw)
    if label == "CARD" and not _luhn_ok(digits):
        return raw  # long numeric ids (Shopify order ids etc.) are not cards
    if label == "PHONE":
        stripped = raw.strip()
        if len(digits) < 9 or len(digits) > 15 or _ISO_DATE.match(stripped):
            return raw  # dates, short references, long system ids
        looks_international = stripped.startswith(("+", "00"))
        has_separator = bool(re.search(r"[ ()\-]", stripped))
        looks_local = stripped.startswith("0") and len(digits) in (9, 10, 11)
        if not (looks_international or has_separator or looks_local):
            return raw  # bare numeric ids such as order or payout numbers
    return f"[REDACTED:{label}]"


def redact_text(text: str) -> str:
    """Replace PII-looking substrings with [REDACTED:<TYPE>]."""
    out = text
    for label, pattern in _PATTERNS:
        out = pattern.sub(lambda m, _l=label: _replace(_l, m), out)
    return out


def redact(value: Any, _key: str | None = None) -> Any:
    """Recursively redact a JSON-like structure (dict/list/str)."""
    if _key is not None and _key.lower() in SENSITIVE_KEYS and value not in (None, ""):
        return "[REDACTED]"
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {k: redact(v, k) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    return value
