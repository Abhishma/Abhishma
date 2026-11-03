# Sync Exception: Shopify-to-ERP sync failure triage

## What it does
Runs on a schedule, reads failed Shopify-to-ERP sync records, classifies each root cause (missing SKU, duplicate order, address/tax error, inventory mismatch, payout mismatch, transient), applies only whitelisted reversible fixes, queues SKU mappings and other changes for approval, and posts an actionable summary to Slack. A deterministic rule layer (triage.py) handles known error strings; the LLM handles confirmation, unknowns, and the write-up.

## Integrations
- Shopify Admin API
- ERPs / accounting: Cin7, Unleashed, MYOB, Xero, NetSuite, QuickBooks, DATEV
- Connectors / middleware whose logs we read: Celigo, A2X, Link My Books, native Cin7/Unleashed integrations
- Slack (chat.postMessage)

## KPIs
- Mean time to resolve sync failures (target: same business day)
- Share of failures auto-fixed safely
- Orders stuck unsynced at month end (target: 0)
- Ops hours saved per week

## Setup
1. Point the TODO adapters in handlers.py at the client's connector error log and ERP item API.
2. Review the SAFE_FIXES whitelist in triage.py with the client; remove any they are not comfortable with.
3. Configure Slack channel and approval flow (Slack buttons or a simple approvals page calling AgentRunner.approve).
4. Schedule (cron / Routine) daily or hourly.

## Guardrails
- Whitelist-only auto-fixes; map_sku requires approval at runner level; any non-whitelisted retry fix returns pending_approval from the handler.
- No edits to money, stock, tax settings or customer data.
- DATEV tax keys and chart-of-accounts issues always go to the bookkeeper.
- max_turns cap prevents runaway retry loops.

## Price (USD)
$7,500-25,000 setup + $900-2,000/month.
