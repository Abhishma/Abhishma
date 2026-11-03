# Compliance Copy Auditor: green claims, price reductions, ad claims, drip pricing

## What it does
Pre-screens product pages, ads, emails and landing pages before publishing. A deterministic rule scan (rules.py) finds candidate issues; the model confirms them in context, drops false positives, adds missed issues, and writes compliant rewrites. Output per finding: exact quote, rule, risk level (high/medium/low) and suggested rewrite, plus a not-legal-advice disclaimer.

Rule sets:
- (a) German / EU EmpCo green-claims bans: klimaneutral / CO2-neutral, generic claims (umweltfreundlich, nachhaltig, eco-friendly), self-made sustainability labels, unqualified biodegradable/compostable
- (b) PAngV section 11 price-reduction wording (30-day lowest price reference)
- (c) Meta ads: unrealistic outcomes, guarantees, personal attributes
- (d) Australian drip pricing (mandatory fees in headline price), plus ACCC environmental claims guidance

## Integrations
Shopify (product descriptions, metafields), Klaviyo (campaigns, flows), Meta Marketing API (ad creatives), Google Docs / Notion briefs, Slack or Airtable for findings.

## KPIs
- High-risk claims caught before publish
- Time to review a batch of 100 product pages (target: under 1 hour including human check)
- Meta ad rejection rate
- Legal review hours saved

## Setup
1. Connect the copy source(s) and implement the TODO adapters in handlers.py.
2. Agree markets per asset (DE/EU, AU, US/CA, NZ) and channels.
3. Review rules.py patterns and rewrite hints with the client's counsel; add brand-specific banned terms.
4. Native German review of German rewrite templates.

## Guardrails
- Deterministic pre-scan always runs; the model cannot skip it.
- Quotes must be exact substrings; rewrites never invent certifications or reference prices.
- Never states copy "is compliant"; disclaimer on every output; high-risk results recommend legal review.

## Price (USD)
$4,000-15,000 (one-off build; optional ongoing monitoring quoted separately).
