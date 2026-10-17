# Marginwise Agents

Production-ready starting points for the AI agents and automations Marginwise builds for ecommerce brands and local service businesses in Australia, New Zealand, the US, Canada, Germany and Saudi Arabia.

Each solution has a system prompt (prompt.md), tool schemas in Anthropic tool-use format (tools.json), mock handlers backed by fixtures with marked TODO adapters for the real APIs (handlers.py, fixtures/), and a client-facing README (what it does, integrations, KPIs, setup, guardrails, price). Everything runs and is tested offline with a scripted FakeClient; real runs use the Anthropic Python SDK when ANTHROPIC_API_KEY is set.

## Solutions

| Solution | Purpose | Key integrations | Price (USD) |
|---|---|---|---|
| [receptionist](solutions/receptionist/README.md) | AI phone/SMS receptionist and missed-call text-back for trades and clinics; AI disclosure, English and German | ServiceM8, simPRO, Tradify, Jobber, Housecall Pro, ServiceTitan, Doctolib-style booking, Twilio | $2,500-6,000 setup + $300-900/mo |
| [whatsapp_commerce](solutions/whatsapp_commerce/README.md) | Arabic/English WhatsApp agent for Saudi D2C: COD confirmation, National Address capture, WISMO, Tabby/Tamara nudge, returns | WhatsApp Cloud API, Salla, Zid, Shopify, SMSA, Aramex, SPL, Tabby, Tamara | $5,000-15,000 + $1,000-3,000/mo |
| [support_wismo](solutions/support_wismo/README.md) | Ecommerce support for order status, returns, exchanges and approved order edits | Shopify, Gorgias, Zendesk, AfterShip, Loop | $9,500-30,000 + $750-2,500/mo |
| [sync_exception](solutions/sync_exception/README.md) | Shopify-to-ERP sync failure triage with whitelisted safe fixes and Slack summary | Cin7, Unleashed, MYOB, Xero, NetSuite, QuickBooks, DATEV, Slack | $7,500-25,000 + $900-2,000/mo |
| [payout_reconciliation](solutions/payout_reconciliation/README.md) | Deterministic payout-to-bank-to-ledger matcher plus plain-English month-end exceptions summary | Shopify Payments, PayPal, Afterpay, Klarna, Stripe, Xero, MYOB, QuickBooks | $2,500-6,000 + $450-1,000/mo |
| [po_to_order](solutions/po_to_order/README.md) | Emailed purchase orders into validated draft sales orders for B2B wholesalers | Gmail, Microsoft 365, Cin7, Unleashed, NetSuite, Xero, Shopify B2B | $6,000-18,000 + $500-1,500/mo |
| [compliance_copy_auditor](solutions/compliance_copy_auditor/README.md) | Audits copy for EmpCo green claims, PAngV price wording, Meta ad claims, AU drip pricing | Shopify, Klaviyo, Meta Marketing API, Google Docs | $4,000-15,000 |
| [gpsr_extractor](solutions/gpsr_extractor/README.md) | Extracts EU GPSR safety fields from supplier documents into Shopify metafields, flags gaps | Shopify metafields, Google Drive, SharePoint | $5,000-20,000 |
| [hs_classifier](solutions/hs_classifier/README.md) | HS code suggestions with confidence and mandatory human review; US/Canada landed-cost calculator | Shopify, USITC HTS, CBSA tariff, Zonos/Avalara | $7,500-18,000 |
| [aeo_visibility](solutions/aeo_visibility/README.md) | Measures brand share of voice in AI assistant answers and reports actions | Anthropic API, OpenAI and Perplexity (stubs), Looker Studio | $1,500-4,000/mo |
| [lead_triage](solutions/lead_triage/README.md) | Inbound lead enrichment, ICP scoring, routing and consent-aware first replies | HubSpot, Salesforce, Apollo/ZoomInfo, Gmail/Outlook | $9,500-30,000 + $1,800-3,500/mo |
| [quote_builder](solutions/quote_builder/README.md) | Instant trade estimates from a price book, site-visit booking, German Angebot | ServiceM8, simPRO, Jobber, Housecall Pro, lexoffice, sevDesk | $3,000-9,000 + $300-800/mo |

## Layout

```
agents/
  core/                 agent runner (dependency-light)
    runner.py           tool-use loop, approval gating, max turns, transcripts
    clients.py          make_client() for the Anthropic SDK; FakeClient for tests
    loader.py           loads prompt.md, tools.json, handlers.py per solution
    guardrails.py       pending-approval objects, light input validation
    redact.py           PII redaction for logs and transcripts
    llm.py              single-call helpers (summaries, cheap classification)
    cli.py              python -m core.cli list | show | run
  solutions/<name>/     prompt.md, tools.json, handlers.py, fixtures/, README.md
  tests/                offline pytest suite
```

## Core runner

- Models: default `claude-sonnet-5-5`; cheap classification `claude-haiku-5-5` (core/llm.py classify). Override with MARGINWISE_MODEL and MARGINWISE_CLASSIFY_MODEL.
- Tool loop: the model's tool calls are validated against the tool's input_schema, dispatched to Python handlers, and all results for a turn are returned in one user message. Handler exceptions become is_error results.
- Guardrails:
  - max_turns (default 10) caps model calls per run.
  - Tools listed in tools.json "requires_approval" never execute in the loop; the model receives a pending_approval object and the request is queued (RunResult.pending_approvals). A human approves later with AgentRunner.approve(approval_id). Handlers can also return pending_approval for unsafe arguments (for example non-whitelisted sync fixes).
  - Transcripts are JSON, written per run when transcript_dir or MARGINWISE_TRANSCRIPT_DIR is set, with emails, phones, card numbers and IBANs redacted. The model-facing conversation is not redacted.
  - Safety refusals stop the run (stop_reason "refusal"). Real Sonnet/Opus calls use the server-side refusal fallback beta (fallbacks="default"); disable with MARGINWISE_SERVER_FALLBACKS=0 on platforms that do not support it.
- Deterministic first: wherever money, tax, consent or compliance logic is involved (payout matching, landed cost, ICP scoring and consent, PO validation, GPSR validation, quote pricing, copy rule scan, National Address validation), the logic lives in plain Python and is unit-tested. The model explains and orchestrates.

## Setup and running

```
cd marginwise/solutions/agents
pip install -r requirements.txt      # anthropic, pytest
python -m pytest                     # offline, no API key needed
python -m core.cli list
python -m core.cli show support_wismo

export ANTHROPIC_API_KEY=...         # real runs
python -m core.cli run receptionist "Hi, my aircon is blowing warm air" \
  --context '{"business_id": "coolbreeze_ac"}' --transcripts ./transcripts --approve
```

Or with make: `make install`, `make test`, `make list`.

## Rules for every client deployment

- Implement the TODO adapters in handlers.py against the client's systems; keep the mock for tests.
- German and Arabic phrases in prompts are starter wording and require native review before go-live.
- Compliance outputs (EmpCo, PAngV, Meta, ACL, GPSR, HS codes, consent) are pre-screens, not legal advice.
- Start every agent in shadow or draft mode, then enable automatic actions one tool at a time.
