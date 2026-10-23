"""Mock handlers for inbound lead triage and speed-to-lead.

TODO(adapters):
  - HubSpot: CRM v3 contacts/companies, owners API, engagements (notes/emails),
    marketing email subscription status for consent
  - Salesforce: Lead / Account SOQL, Lead.OwnerId update, Task insert
  - Enrichment: Clearbit-style / Apollo / ZoomInfo company lookup, BuiltWith or
    Wappalyzer for tech stack
  - Email drafts: HubSpot single-send drafts, Gmail/Outlook drafts for the owner
"""

from __future__ import annotations

import uuid
from pathlib import Path

from core.fixtures import load_json, not_found, now

from .scoring import check_consent, score_lead as _score

FIXTURES = Path(__file__).parent / "fixtures"
LEADS = load_json(FIXTURES / "leads.json")
COMPANIES = load_json(FIXTURES / "companies.json")
ICP = load_json(FIXTURES / "icp.json")
OWNERS = load_json(FIXTURES / "owners.json")
STATE: dict = {"assignments": {}, "drafts": [], "activities": []}


def reset_state() -> None:
    STATE["assignments"].clear()
    STATE["drafts"].clear()
    STATE["activities"].clear()


def get_lead(lead_id: str) -> dict:
    lead = LEADS.get(lead_id)
    return {"found": True, **lead} if lead else not_found("lead", lead_id)


def enrich_company(domain: str) -> dict:
    c = COMPANIES.get((domain or "").lower())
    if not c:
        return {"found": False, "domain": domain, "note": "no enrichment data; score on form data only"}
    return {"found": True, "domain": domain, **c}


def score_lead(lead_id: str) -> dict:
    lead = LEADS.get(lead_id)
    if not lead:
        return not_found("lead", lead_id)
    company = COMPANIES.get((lead.get("company_domain") or "").lower())
    return {"lead_id": lead_id, **_score(lead, company, ICP)}


def assign_owner(lead_id: str, tier: str, owner_id: str = "") -> dict:
    lead = LEADS.get(lead_id)
    if not lead:
        return not_found("lead", lead_id)
    if tier == "DQ":
        return {"assigned": False, "reason": "disqualified leads are not routed; log activity instead"}
    target = owner_id or ("nurture_queue" if tier == "C" else OWNERS["routing"].get(lead["market"], "nurture_queue"))
    if target not in OWNERS["owners"]:
        return {"assigned": False, "error": f"unknown owner {target}"}
    STATE["assignments"][lead_id] = target
    return {"assigned": True, "lead_id": lead_id, "owner_id": target, **OWNERS["owners"][target]}


def draft_email(lead_id: str, email_type: str, subject: str, body: str, language: str = "en") -> dict:
    """Requires human approval (runner gate). Re-checks consent and content before saving a draft."""
    lead = LEADS.get(lead_id)
    if not lead:
        return not_found("lead", lead_id)
    consent = check_consent(lead, email_type, now().date())
    if not consent["allowed"]:
        return {"drafted": False, "error": "consent check failed", "consent": consent}
    lower = body.lower()
    if email_type == "marketing_followup" and "unsubscribe" not in lower and "abmelden" not in lower:
        return {"drafted": False, "error": "marketing email must contain an unsubscribe line", "consent": consent}
    did = f"EML-{uuid.uuid4().hex[:6].upper()}"
    STATE["drafts"].append({"draft_id": did, "lead_id": lead_id, "type": email_type, "subject": subject,
                            "body": body, "language": language})
    return {"drafted": True, "draft_id": did, "consent": consent}


def log_activity(lead_id: str, activity_type: str, summary: str) -> dict:
    STATE["activities"].append({"lead_id": lead_id, "type": activity_type, "summary": summary})
    return {"logged": True, "lead_id": lead_id, "activity_type": activity_type}


HANDLERS = {
    "get_lead": get_lead,
    "enrich_company": enrich_company,
    "score_lead": score_lead,
    "assign_owner": assign_owner,
    "draft_email": draft_email,
    "log_activity": log_activity,
}
