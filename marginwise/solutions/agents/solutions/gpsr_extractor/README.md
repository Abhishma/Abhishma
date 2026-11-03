# GPSR Extractor: EU product safety fields into Shopify metafields

## What it does
Reads supplier PDFs, spec sheets and emails, extracts the EU GPSR online-listing fields (manufacturer name, postal address, email; EU responsible person name, address, email; product type/batch identifier; warnings and safety information), validates completeness deterministically (EU/EEA address check for the responsible person, German warnings for DE), flags missing fields with a ready-to-send supplier request, and prepares Shopify metafields JSON (namespace gpsr) for approval.

## Integrations
- Shopify Admin GraphQL (metafield definitions + metafieldsSet), theme block to display the fields
- Document sources: Google Drive, SharePoint, Gmail/Outlook attachments; PDF text extraction
- Optional: Airtable / Sheets supplier compliance tracker

## KPIs
- Share of EU-sold SKUs with complete GPSR data
- Days to close supplier data gaps
- Marketplace listing suppressions due to missing GPSR data (Amazon, eBay, Etsy, Zalando)
- Hours of manual data entry saved per 100 SKUs

## Setup
1. Create metafield definitions (gpsr.manufacturer_name, ... gpsr.warnings) and a product page block.
2. Collect supplier documents per SKU; implement the TODO adapters in handlers.py.
3. Run in batches; review pending approvals; send generated supplier requests.

## Guardrails
- Values must appear verbatim in the source; nulls are flagged, never guessed.
- write_metafields requires human approval.
- EU responsible person must have an EU/EEA address; WeChat/WhatsApp is not an electronic address.
- Not legal advice; sector rules (toys, electricals, cosmetics) are escalated.

## Price (USD)
$5,000-20,000 (one-off, depending on SKU count and document quality).
