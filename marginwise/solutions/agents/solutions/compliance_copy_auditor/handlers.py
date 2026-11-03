"""Mock handlers for the compliance copy auditor.

TODO(adapters):
  - Copy sources: Shopify Admin API (product descriptionHtml, metafields), Klaviyo
    campaigns/templates API, Meta Marketing API (ad creatives), Google Docs / Notion
  - Findings sink: Google Sheets, Airtable, Notion database, or a Slack review channel
"""

from __future__ import annotations

import uuid
from pathlib import Path

from core.fixtures import load_json, not_found

from .rules import DISCLAIMER, scan

FIXTURES = Path(__file__).parent / "fixtures"
COPY = load_json(FIXTURES / "copy.json")
STATE: dict[str, list] = {"audits": []}


def reset_state() -> None:
    STATE["audits"].clear()


def get_copy(asset_id: str) -> dict:
    asset = COPY.get(asset_id)
    return {"found": True, **asset} if asset else not_found("asset", asset_id)


def scan_rules(text: str, markets: list, channel: str = "web") -> dict:
    hits = scan(text, markets, channel)
    return {"candidate_count": len(hits), "candidates": hits,
            "note": "Candidates only: confirm each in context, drop false positives, add missed issues."}


def record_findings(asset_id: str, findings: list, overall_risk: str) -> dict:
    required = {"quote", "rule", "risk", "suggested_rewrite"}
    bad = [i for i, f in enumerate(findings) if not isinstance(f, dict) or not required <= set(f)]
    if bad:
        return {"recorded": False, "error": f"findings {bad} missing one of {sorted(required)}"}
    audit_id = f"AUD-{uuid.uuid4().hex[:6].upper()}"
    STATE["audits"].append({"audit_id": audit_id, "asset_id": asset_id, "findings": findings,
                            "overall_risk": overall_risk, "disclaimer": DISCLAIMER})
    return {"recorded": True, "audit_id": audit_id, "disclaimer": DISCLAIMER}


HANDLERS = {"get_copy": get_copy, "scan_rules": scan_rules, "record_findings": record_findings}
