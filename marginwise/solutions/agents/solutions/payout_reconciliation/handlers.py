"""Handlers for the payout reconciliation summary step.

The reconciliation itself is deterministic (matcher.py). In agent mode the
model can fetch the report and the exception list through these tools; in
the simpler single-call mode, summarize.write_summary passes the report JSON
directly.

TODO(adapters): replace the fixture folder with real exports:
  - Shopify Payments: GraphQL shopifyPaymentsAccount.balanceTransactions / payouts
  - PayPal: Transaction Search API (/v1/reporting/transactions)
  - Afterpay: Settlements API; Klarna: Settlements API (/settlements/v1/transactions)
  - Stripe: Reporting API report type payout_reconciliation.itemized.5
  - Bank: Basiq / Akahu (AU/NZ), Plaid (US/CA), finAPI (DE), or Xero bank feed export
  - Accounting: Xero / MYOB / QuickBooks journals for the clearing accounts
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .matcher import reconcile_files

FIXTURES = Path(__file__).parent / "fixtures"
_CACHE: dict[str, dict] = {}


def _report(period: str) -> dict:
    if period not in _CACHE:
        year, month = (int(x) for x in period.split("-"))
        end = date(year + (month == 12), month % 12 + 1, 1)
        period_end = date.fromordinal(end.toordinal() - 1)
        _CACHE[period] = reconcile_files(FIXTURES, period=period, period_end=period_end).to_dict()
    return _CACHE[period]


def get_reconciliation_report(period: str) -> dict:
    report = _report(period)
    return {k: v for k, v in report.items() if k != "exceptions"} | {"exception_count": len(report["exceptions"])}


def list_exceptions(period: str, severity: str = "") -> dict:
    exc = _report(period)["exceptions"]
    if severity:
        exc = [e for e in exc if e["severity"] == severity]
    return {"period": period, "count": len(exc), "exceptions": exc}


HANDLERS = {
    "get_reconciliation_report": get_reconciliation_report,
    "list_exceptions": list_exceptions,
}
