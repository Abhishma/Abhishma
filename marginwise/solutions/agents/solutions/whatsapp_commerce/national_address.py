"""Saudi National Address short-code validation (deterministic, offline).

The National Address "short address" is 8 characters: 4 letters followed by
4 digits, for example RRRD2929. Customers often type it with spaces, dashes,
lower case, or Arabic-Indic digits, so we normalise before validating.

Format validation only proves the code is well formed. Whether it resolves to
a real building must be checked against Saudi Post / SPL National Address API.
TODO(adapter): call the SPL National Address API (address.gov.sa developer
portal) to resolve the short code to building number, street, district, city,
postal code and additional number, and compare the city to the order city.

The region-letter table below is a best-effort hint for routing and sanity
checks, NOT authoritative. Confirm it with SPL before relying on it.
"""

from __future__ import annotations

import re

_ARABIC_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_SHORT = re.compile(r"^[A-Z]{4}[0-9]{4}$")

# First letter -> region hint (unverified; see module docstring).
REGION_HINTS = {
    "R": "Riyadh",
    "M": "Makkah",
    "D": "Eastern Province",
    "Q": "Qassim",
}


def normalize_short_address(raw: str) -> str:
    """Uppercase, convert Arabic-Indic digits, drop spaces/dashes/dots."""
    text = (raw or "").translate(_ARABIC_INDIC).upper()
    return re.sub(r"[\s\-_.]", "", text)


def validate_short_address(raw: str) -> dict:
    """Validate a National Address short code.

    Returns {"valid": bool, "normalized": str, "errors": [...], "region_hint": str|None}
    """
    norm = normalize_short_address(raw)
    errors: list[str] = []
    if not norm:
        errors.append("empty")
    elif re.search(r"[؀-ۿ]", norm):
        errors.append("contains Arabic letters; short address letters are Latin A-Z")
    elif len(norm) != 8:
        errors.append(f"must be 8 characters (4 letters + 4 digits), got {len(norm)}")
    elif not _SHORT.match(norm):
        errors.append("must be 4 letters followed by 4 digits, e.g. RRRD2929")
    elif norm[4:] == "0000":
        errors.append("digits cannot be 0000")
    valid = not errors
    return {
        "valid": valid,
        "normalized": norm,
        "errors": errors,
        "region_hint": REGION_HINTS.get(norm[0]) if valid else None,
        "note": "Format check only; resolve via SPL National Address API before dispatch.",
    }


def validate_full_address(building_number: str, postal_code: str, additional_number: str = "") -> dict:
    """Validate the long-form components that accompany a National Address."""
    errors = []
    b = (building_number or "").translate(_ARABIC_INDIC).strip()
    p = (postal_code or "").translate(_ARABIC_INDIC).strip()
    a = (additional_number or "").translate(_ARABIC_INDIC).strip()
    if not re.fullmatch(r"\d{4}", b):
        errors.append("building number must be 4 digits")
    if not re.fullmatch(r"\d{5}", p):
        errors.append("postal code must be 5 digits")
    if a and not re.fullmatch(r"\d{4}", a):
        errors.append("additional number must be 4 digits")
    return {"valid": not errors, "errors": errors}
