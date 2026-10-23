# Lead Triage: inbound lead scoring, routing and speed-to-lead replies

## What it does
When a lead lands in HubSpot or Salesforce, the agent enriches the company, scores it deterministically against the ICP (revenue band, stack, market, intent, industry), routes it to the regional owner or nurture queue, drafts a first reply in the lead's language and market tone (owner approval required), and logs everything to the CRM. Consent rules for AU (Spam Act), NZ (UEMA), CA (CASL), DE (UWG section 7, double opt-in), US (CAN-SPAM) and SA are enforced in code before any draft is saved.

## Integrations
HubSpot or Salesforce; enrichment (Apollo, ZoomInfo, Clearbit-style APIs, BuiltWith/Wappalyzer); Gmail/Outlook or HubSpot email drafts; Slack alerts for tier A; calendar links (HubSpot Meetings, Calendly).

## KPIs
- Median time to first response (target under 5 minutes, business hours)
- Lead-to-meeting rate for tier A/B
- Share of leads triaged without human touch
- Consent violations (target: 0)

## Setup
1. Agree ICP weights (fixtures/icp.json) and routing (owners.json) with sales leadership.
2. Map CRM consent fields (opt-in, double opt-in timestamp, inquiry date) and implement TODO adapters.
3. Load approved proof points and pricing ranges into runtime context.
4. Shadow mode for two weeks: drafts only, compare scores with rep judgment, then tune weights.

## Guardrails
- draft_email requires approval and re-checks consent and unsubscribe content.
- DQ leads are never routed or emailed.
- No invented case studies, pricing commitments or guessed contact data.
- Unsubscribe, data-access and deletion requests are flagged to compliance.

## Price (USD)
$9,500-30,000 setup + $1,800-3,500/month.
