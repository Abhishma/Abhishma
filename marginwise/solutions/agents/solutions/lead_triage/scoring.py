"""Deterministic ICP scoring and consent checks for inbound leads."""

from __future__ import annotations

from datetime import date


def score_lead(lead: dict, company: dict | None, icp: dict) -> dict:
    """Score 0-100 against the ICP. Returns score, tier (A/B/C/DQ) and reasons."""
    reasons: list[str] = []
    company = company or {}
    flags = set(company.get("flags", [])) | set(lead.get("flags", []))
    dq = flags & set(icp["disqualify_flags"])
    if dq:
        return {"score": 0, "tier": "DQ", "reasons": [f"disqualified: {', '.join(sorted(dq))}"]}

    score = 0
    band = company.get("revenue_band")
    pts = icp["revenue_band_points"].get(band, 0) if band else 0
    score += pts
    reasons.append(f"revenue band {band or 'unknown'}: +{pts}")

    stack_pts = sum(icp["stack_points"].get(t, 0) for t in company.get("stack", []))
    stack_pts = min(stack_pts, icp["stack_cap"])
    score += stack_pts
    reasons.append(f"stack {company.get('stack', [])}: +{stack_pts}")

    mpts = icp["market_points"].get(lead.get("market", ""), 0)
    score += mpts
    reasons.append(f"market {lead.get('market')}: +{mpts}")

    ipts = icp["intent_points"].get(lead.get("form_type", ""), 0)
    score += ipts
    reasons.append(f"intent {lead.get('form_type')}: +{ipts}")

    industry = company.get("industry", "")
    if any(industry.startswith(p) for p in icp["industry_prefixes"]):
        score += icp["industry_points"]
        reasons.append(f"industry {industry}: +{icp['industry_points']}")

    domain = (lead.get("email", "").split("@")[-1]).lower()
    if domain in icp["free_email_domains"]:
        score += icp["free_email_penalty"]
        reasons.append(f"free email domain: {icp['free_email_penalty']}")

    score = max(0, min(100, score))
    tier = "A" if score >= icp["tiers"]["A"] else "B" if score >= icp["tiers"]["B"] else "C"
    return {"score": score, "tier": tier, "reasons": reasons}


def check_consent(lead: dict, email_type: str, today: date) -> dict:
    """Decide whether an email of this type may be sent, and what it must contain.

    email_type:
      inquiry_response    a direct, one-to-one answer to the lead's own request
      marketing_followup  anything promotional beyond answering the request

    Rules (simplified; confirm with counsel per client):
      AU Spam Act 2003: commercial messages need consent (express or inferred),
        sender identification and a functional unsubscribe.
      CA CASL: express consent, or implied consent (inquiry within 6 months,
        purchase within 2 years); identification and unsubscribe required.
      DE UWG section 7: email advertising needs prior express consent; use
        double opt-in as proof. A reply to the request must not add advertising.
      US CAN-SPAM: opt-out model; identification, physical address, unsubscribe.
      SA: treat as express consent required (PDPL and telecom anti-spam rules).
    """
    market = lead.get("market", "")
    c = lead.get("consent", {}) or {}
    required = ["sender name and company", "reply-to address"]
    reasons: list[str] = []

    if email_type == "inquiry_response":
        allowed = True
        reasons.append("direct reply to the lead's own inquiry")
        if not lead.get("message") and lead.get("form_type") == "newsletter_signup":
            allowed = False
            reasons.append("no inquiry to respond to (newsletter signup)")
        if market == "DE":
            reasons.append("DE: answer the request only; no additional advertising content")
        return {"allowed": allowed, "email_type": email_type, "reasons": reasons, "required_elements": required}

    if email_type != "marketing_followup":
        return {"allowed": False, "email_type": email_type, "reasons": ["unknown email type"], "required_elements": required}

    required += ["unsubscribe link"]
    opt_in = bool(c.get("marketing_opt_in"))
    if market == "AU" or market == "NZ":
        allowed = opt_in
        reasons.append("Spam Act (AU) / UEMA (NZ): consent required" + ("" if opt_in else "; none recorded"))
    elif market == "CA":
        implied = False
        if c.get("inquiry_date"):
            days = (today - date.fromisoformat(c["inquiry_date"])).days
            implied = days <= 183
            reasons.append(f"CASL implied consent from inquiry {days} days ago ({'valid' if implied else 'expired'})")
        allowed = opt_in or implied
    elif market == "DE":
        allowed = opt_in and bool(c.get("double_opt_in_confirmed"))
        reasons.append("UWG section 7: express consent with double opt-in required"
                       + ("" if allowed else "; double opt-in not confirmed"))
    elif market == "US":
        allowed = True
        required += ["physical postal address"]
        reasons.append("CAN-SPAM opt-out model")
    elif market == "SA":
        allowed = opt_in
        reasons.append("SA: express consent required" + ("" if opt_in else "; none recorded"))
    else:
        allowed = opt_in
        reasons.append("unknown market: require express consent")
    return {"allowed": allowed, "email_type": email_type, "reasons": reasons, "required_elements": required}
