# Support WISMO: order status, returns, exchanges and order edits

## What it does
First-line ecommerce support agent for Shopify stores, running inside Gorgias or Zendesk. Verifies the customer (order number + email), answers where-is-my-order questions from live tracking, creates returns and exchanges within policy, requests address edits on unfulfilled orders (human-approved), writes an internal note on every ticket, and escalates everything else with a summary.

## Integrations
- Shopify Admin GraphQL (orders, order edits, returns)
- Gorgias or Zendesk (ticket replies, internal notes, routing)
- Tracking: AfterShip / Shippo or carrier APIs (UPS, USPS, FedEx, Canada Post, AusPost, DHL)
- Optional returns apps: Loop, Redo, AfterShip Returns

## KPIs
- Automated resolution rate on WISMO / return / exchange tickets (target 50-70%)
- First response time (target under 2 minutes)
- Exchange-instead-of-refund rate (revenue retained)
- CSAT on AI-resolved tickets vs human
- Escalation accuracy (escalated tickets that truly needed a human)

## Setup
1. Connect Shopify and helpdesk APIs; implement the TODO adapters in handlers.py.
2. Encode the store's return/exchange policy in fixtures/shop.json shape (window, final-sale tags, free-return reasons, label fee).
3. Start in draft mode: the agent writes replies as internal drafts for 1-2 weeks, humans send.
4. Switch WISMO to auto-send first, then returns/exchanges.

## Guardrails
- Identity check before any order data is shared.
- edit_order_address requires human approval (runner returns pending_approval).
- Policy (windows, final sale) enforced in code; no refunds, credits or discounts by the agent.
- EU 14-day withdrawal and AU consumer guarantees force escalation instead of refusal.
- Transcripts PII-redacted.

## Price (USD)
$9,500-30,000 setup + $750-2,500/month.
