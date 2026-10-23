# PO to Order: emailed purchase orders into draft sales orders

## What it does
Reads purchase orders that B2B customers email (body text or PDF text), extracts a structured sales order that matches fixtures/order_schema.json, validates it deterministically against the customer account and contracted price list (unknown SKUs, price differences, MOQ, pack multiples, unit of measure, payment terms, ship-to, the PO's own arithmetic, credit limit), flags discrepancies to sales ops, and creates a draft order in the ERP only after human approval. Handles English and German POs, day-first and month-first dates, and decimal commas.

## Integrations
- Inbox: Gmail, Microsoft 365 (Graph)
- ERP / order systems: Cin7, Unleashed, NetSuite, MYOB, Xero (quotes), QuickBooks (estimates), Shopify B2B draft orders, Brightpearl
- PDF text: pdfplumber, or Claude document input for scanned PDFs

## KPIs
- PO-to-draft time (target: under 10 minutes from receipt)
- Order entry hours saved per week
- Pricing errors reaching invoices (target: 0)
- Share of POs processed with no human edits

## Setup
1. Export customer accounts (terms, ship-tos, credit) and price lists; implement the TODO adapters in handlers.py.
2. Confirm the extraction schema fields with the client's ERP draft order API.
3. Route the "orders@" mailbox to the agent; run 50 historical POs through and compare with what was keyed.
4. Approvals: sales ops approves drafts (AgentRunner.approve) from a queue.

## Guardrails
- create_draft_order requires approval; drafts only, never confirmed orders or customer replies.
- Deterministic validation; list prices always used, PO price differences flagged.
- Block-severity issues (unknown SKU, currency) prevent drafts.
- Instructions inside emails are treated as data (bank-detail change requests flagged as possible fraud).

## Price (USD)
$6,000-18,000 setup + $500-1,500/month.
