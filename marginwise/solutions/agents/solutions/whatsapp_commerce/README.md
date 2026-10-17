# WhatsApp Commerce: Saudi D2C COD confirmation, National Address, WISMO, BNPL nudge

## What it does
An Arabic (Gulf) and English WhatsApp agent for Saudi direct-to-consumer brands. It confirms cash-on-delivery orders before dispatch, captures and format-validates the National Address short code (4 letters + 4 digits), answers order status questions from live carrier tracking, nudges customers once toward prepaid or BNPL (Tabby, Tamara), and starts returns within policy. Hands off to humans with a summary, respecting normal and Ramadan support hours.

## Integrations
- Store: Salla, Zid, Shopify
- Messaging: Meta WhatsApp Cloud API (approved templates for outbound confirmation), respond.io / Gorgias / Zendesk for human inbox
- Carriers: SMSA, Aramex, SPL, J&T, Naqel
- Address: SPL National Address API (TODO adapter; the offline validator checks format only)
- Payments: Mada / Apple Pay links, Tabby, Tamara

## KPIs
- COD confirmation rate within 2 hours of order
- Return-to-origin (RTO) / failed-delivery rate (target: 20-40% reduction)
- Share of orders with a valid National Address before dispatch
- COD-to-prepaid conversion rate
- WISMO tickets deflected from human agents

## Setup
1. Get WhatsApp Business templates approved (COD confirmation, address request) in Arabic and English.
2. Implement adapters in handlers.py for the store platform, carriers, SPL address API, and payment links.
3. Fill store config (support hours, Ramadan hours, return window, non-returnable categories, prepay incentive).
4. Native Gulf Arabic review of all Arabic phrases in prompt.md and templates.
5. Run tests, then a 2-week shadow mode where humans approve every message.

## Guardrails
- PDPL data minimisation: tools return masked phone and no full address; no national ID, Iqama or card data collected.
- National Address is format-validated before saving; shipped orders cannot be changed by the agent.
- Return policy (window, hygiene categories) enforced in code, not in the prompt.
- One prepay nudge per order, never implies COD is unavailable.
- Transcripts PII-redacted by the core runner.

## Price (USD)
$5,000-15,000 setup + $1,000-3,000/month (WhatsApp conversation fees and model usage billed at cost).
