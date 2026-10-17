# HS Classifier: HS code suggestions and US/Canada landed cost

## What it does
Suggests six-digit HS codes for products with confidence and rationale, explains what decides the national 8/10-digit line (US HTSUS, Canadian Customs Tariff), and always routes suggestions to a human customs reviewer. Includes a deterministic landed-cost calculator (landed_cost.py) for US and Canada cross-border workflows: duty rate input, tariff surcharge input, freight, insurance, FX, US MPF/HMF, Canadian GST/HST, broker fee, per-unit cost.

## Integrations
- Shopify (inventory item harmonized_system_code and country_code_of_origin, written only after review)
- Tariff data: USITC HTS, CBSA Customs Tariff, or providers such as Zonos, Avalara, Descartes
- Review queue: Airtable, Google Sheets, Linear
- Shipping: Easyship, ShipStation, Starshipit (DDP/DDU settings)

## KPIs
- SKUs with reviewed HS codes and origin (target: 100% of cross-border catalogue)
- Broker queries / customs holds per month
- Landed-cost accuracy vs actual broker invoices (target within 3%)
- Reviewer time per SKU

## Setup
1. Export products with materials and origin; implement TODO adapters in handlers.py.
2. Agree the reviewer (licensed customs broker or trade specialist) and the review queue.
3. Load current duty and surcharge rates per national line at review time; confirm US MPF min/max for the fiscal year.
4. Run on the catalogue in batches; reviewer approves; approved codes are written to Shopify.

## Guardrails
- submit_for_review is mandatory; nothing is applied automatically.
- No rates are guessed; the calculator only uses supplied rates.
- Refuses undervaluation, origin or description misdeclaration.
- Not customs brokerage or legal advice.

## Price (USD)
$7,500-18,000 (one-off, catalogue size dependent).
