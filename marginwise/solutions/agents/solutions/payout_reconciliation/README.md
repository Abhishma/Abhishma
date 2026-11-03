# Payout Reconciliation: provider payouts vs bank vs ledger

## What it does
A deterministic matcher (matcher.py, pure Python, Decimal arithmetic) parses Shopify Payments, PayPal, Afterpay, Klarna and Stripe payout exports, groups them into payouts, and matches each payout to a bank statement line and to its accounting clearing entry. It computes sales, refunds, chargebacks, fees, effective fee rate, FX variance on cross-currency payouts, and lists every unmatched or mismatched item as a typed exception. An LLM step (summarize.py + prompt.md) then writes a plain-English month-end exceptions summary from the JSON, without computing any numbers itself. A deterministic fallback summary is available offline.

## Integrations
- Providers: Shopify Payments, PayPal, Afterpay/Clearpay, Klarna, Stripe
- Bank data: Basiq / Akahu (AU/NZ), Plaid (US/CA), finAPI (DE), or bank CSV / Xero bank feed export
- Accounting: Xero, MYOB, QuickBooks (clearing account journals); A2X / Link My Books postings

## KPIs
- Days to close the month for payment clearing accounts
- Unexplained clearing account balance at month end (target: 0)
- Exceptions caught per month (fees, chargebacks, short settlements)
- Bookkeeper hours saved

## Setup
1. Export one month of each provider report, the bank statement and the clearing account transactions into a folder with the same file names as fixtures/.
2. Set fx_rates.json reference rates (e.g. RBA / ECB month-end rates) and the bank currency.
3. Run: python -c "from solutions.payout_reconciliation.matcher import reconcile_files; ..." or wire the TODO adapters in handlers.py for API pulls.
4. Optional: run the summary with a real client (summarize.write_summary(report, client)).

## Guardrails
- All matching and arithmetic is deterministic and unit-tested; the LLM never computes figures.
- One-to-one matching; ambiguous lines are left unmatched rather than force-matched.
- FX matches require a reference rate and a tolerance band (default 3%); variance above 0.75% is flagged.
- No ledger writes; the output is a report for a human bookkeeper.

## Price (USD)
$2,500-6,000 setup + $450-1,000/month.
