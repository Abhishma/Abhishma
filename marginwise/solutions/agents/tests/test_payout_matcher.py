"""Thorough tests for the deterministic payout reconciliation matcher."""

from datetime import date
from decimal import Decimal

import pytest

from core import FakeClient, fake_text
from solutions.payout_reconciliation import matcher as m
from solutions.payout_reconciliation.handlers import get_reconciliation_report, list_exceptions
from solutions.payout_reconciliation.summarize import fallback_summary, summary_input, write_summary

FIX = m.Path(__file__).resolve().parent.parent / "solutions" / "payout_reconciliation" / "fixtures"


@pytest.fixture(scope="module")
def report():
    return m.reconcile_files(FIX, bank_currency="AUD", period="2026-09", period_end=date(2026, 9, 30))


def _match(report, payout_id):
    return next(x for x in report.matches if x.payout_id == payout_id)


def _exc(report, kind):
    return [e for e in report.exceptions if e.kind == kind]


# ---------------------------------------------------------------- parsers

def test_parse_shopify_lines_and_signs():
    lines = m.parse_shopify(FIX / "shopify_payouts.csv")
    assert len(lines) == 7
    cb = next(l for l in lines if l.kind == "chargeback")
    assert cb.gross == Decimal("-110.00") and cb.fee == Decimal("25.00") and cb.net == Decimal("-135.00")
    assert all(l.net == l.gross - l.fee for l in lines)


def test_parse_paypal_groups_by_withdrawal_and_excludes_pending():
    lines, declared, pending = m.parse_paypal(FIX / "paypal_activity.csv")
    assert {l.payout_id for l in lines} == {"WD-7Y1", "WD-8K2"}
    assert declared == {"WD-7Y1": Decimal("490.90"), "WD-8K2": Decimal("74.47")}
    assert [r["Transaction ID"] for r in pending] == ["6FG78901HI234567J"]
    first = [l for l in lines if l.payout_id == "WD-7Y1"]
    assert sum(l.net for l in first) == Decimal("490.90")
    assert first[0].fee == Decimal("7.28")  # PayPal negative fee becomes a positive cost


def test_parse_klarna_fee_rows():
    lines = m.parse_klarna(FIX / "klarna_settlements.csv")
    fee = next(l for l in lines if l.kind == "fee")
    assert fee.gross == 0 and fee.fee == Decimal("16.30") and fee.net == Decimal("-16.30")
    assert sum(l.net for l in lines) == Decimal("323.70")


def test_parse_stripe_presentment_currency():
    lines = m.parse_stripe(FIX / "stripe_payout_reconciliation.csv")
    usd = next(l for l in lines if l.presentment_currency == "USD")
    assert usd.currency == "AUD" and usd.gross == Decimal("152.00") and usd.presentment_amount == Decimal("100.00")


def test_parse_from_raw_text():
    text = "Settlement Date,Settlement ID,Order ID,Type,Order Amount,Merchant Fee,Net Amount,Currency\n" \
           "2026-09-01,AP-1,#1,Sale,100.00,6.30,93.70,AUD\n"
    lines = m.parse_afterpay(text)
    assert lines[0].net == Decimal("93.70")


# ------------------------------------------------------------- aggregates

def test_payout_aggregates(report):
    p = next(p for p in report.payouts if p.payout_id == "P-SHP-1001")
    assert p.gross_sales == Decimal("209.95")
    assert p.refunds == Decimal("-45.00")
    assert p.fees == Decimal("4.27")
    assert p.net == Decimal("160.68")


def test_totals_per_provider(report):
    t = report.to_dict()["totals"]
    assert t["shopify:AUD"]["payouts"] == 3 and t["shopify:AUD"]["matched"] == 2
    assert t["shopify:AUD"]["chargebacks"] == "-110.00"
    assert t["paypal:USD"]["fx_variance_bank_ccy"] == "-7.66"
    assert t["stripe:AUD"]["effective_fee_rate_pct"] == "3.12"
    assert t["klarna:AUD"]["fees"] == "16.30"


# --------------------------------------------------------------- matching

def test_exact_bank_matches(report):
    for pid in ("P-SHP-1001", "P-SHP-1002", "AP-77001", "po_1Stripe01"):
        assert _match(report, pid).match_type == "exact"
    assert _match(report, "P-SHP-1001").bank_line_id == "BANK-0002"
    assert _match(report, "P-SHP-1002").days_to_bank == 1


def test_fx_match_and_variance(report):
    wd = _match(report, "WD-7Y1")
    assert wd.match_type == "fx"
    assert wd.bank_amount == Decimal("733.85")
    assert wd.difference == Decimal("-7.41")  # 490.90 * 1.51 = 741.26 expected
    fx = _exc(report, "fx_variance")
    assert [e.reference for e in fx] == ["WD-7Y1"]  # WD-8K2 (-0.25) is under the flag threshold


def test_amount_mismatch_with_reference(report):
    k = _match(report, "KL-5501")
    assert k.match_type == "amount_mismatch" and k.difference == Decimal("-3.00")
    exc = _exc(report, "bank_amount_mismatch")
    assert exc[0].severity == "high" and exc[0].amount == Decimal("-3.00")


def test_unmatched_payout_in_transit_is_low_severity(report):
    exc = [e for e in _exc(report, "unmatched_payout") if e.reference == "P-SHP-1003"]
    assert exc and exc[0].severity == "low"


def test_unmatched_bank_line_and_ignored_lines(report):
    assert [b.amount for b in report.unmatched_bank_lines] == [Decimal("55.00")]
    assert report.ignored_bank_lines == 2  # rent and savings transfer


def test_accounting_matching(report):
    assert _match(report, "P-SHP-1002").accounting_difference == Decimal("135.00")
    assert _exc(report, "accounting_mismatch")[0].reference == "P-SHP-1002"
    missing = {e.reference for e in _exc(report, "missing_in_accounting")}
    assert missing == {"po_1Stripe01", "P-SHP-1003"}
    orphan = _exc(report, "accounting_entry_without_payout")
    assert [e.reference for e in orphan] == ["P-SHP-0999"]


def test_chargebacks_and_pending_reported(report):
    cbs = {(e.provider, e.reference) for e in _exc(report, "chargeback")}
    assert cbs == {("shopify", "#0975"), ("paypal", "#1004")}
    assert _exc(report, "pending_provider_balance")[0].amount == Decimal("72.10")


def test_one_to_one_matching_with_duplicate_amounts():
    """Two identical payouts must not both claim the same bank line."""
    lines = [
        m.PayoutLine("stripe", "po_A", date(2026, 9, 1), "charge", "#1", Decimal("100"), Decimal("3"), Decimal("97"), "AUD"),
        m.PayoutLine("stripe", "po_B", date(2026, 9, 8), "charge", "#2", Decimal("100"), Decimal("3"), Decimal("97"), "AUD"),
    ]
    bank = [m.BankLine("B1", date(2026, 9, 2), "STRIPE", Decimal("97"), "AUD"),
            m.BankLine("B2", date(2026, 9, 9), "STRIPE", Decimal("97"), "AUD")]
    rep = m.reconcile(lines, bank, [], cfg=m.MatchConfig(bank_currency="AUD"))
    got = {x.payout_id: x.bank_line_id for x in rep.matches}
    assert got == {"po_A": "B1", "po_B": "B2"}


def test_date_window_enforced():
    lines = [m.PayoutLine("shopify", "P1", date(2026, 9, 1), "charge", "#1", Decimal("50"), Decimal("1"), Decimal("49"), "AUD")]
    bank = [m.BankLine("B1", date(2026, 9, 20), "SHOPIFY", Decimal("49"), "AUD")]
    rep = m.reconcile(lines, bank, [], cfg=m.MatchConfig(bank_currency="AUD"))
    assert rep.matches[0].match_type == "none"
    assert {e.kind for e in rep.exceptions} >= {"unmatched_payout", "unmatched_bank_line"}


def test_provider_keyword_required():
    lines = [m.PayoutLine("klarna", "K1", date(2026, 9, 1), "charge", "#1", Decimal("80"), Decimal("0"), Decimal("80"), "AUD")]
    bank = [m.BankLine("B1", date(2026, 9, 2), "SHOPIFY PAYMENTS", Decimal("80"), "AUD")]
    rep = m.reconcile(lines, bank, [], cfg=m.MatchConfig(bank_currency="AUD"))
    assert rep.matches[0].match_type == "none"


def test_fx_outside_tolerance_does_not_match():
    lines = [m.PayoutLine("paypal", "W1", date(2026, 9, 1), "charge", "#1", Decimal("100"), Decimal("0"), Decimal("100"), "USD")]
    bank = [m.BankLine("B1", date(2026, 9, 2), "PAYPAL", Decimal("120"), "AUD")]  # expected 151
    rep = m.reconcile(lines, bank, [], fx_rates={"USD/AUD": "1.51"}, cfg=m.MatchConfig(bank_currency="AUD"))
    assert rep.matches[0].match_type == "none"


def test_inverse_fx_rate_used():
    lines = [m.PayoutLine("stripe", "S1", date(2026, 9, 1), "charge", "#1", Decimal("100"), Decimal("0"), Decimal("100"), "AUD")]
    bank = [m.BankLine("B1", date(2026, 9, 2), "STRIPE", Decimal("66.20"), "USD")]
    rep = m.reconcile(lines, bank, [], fx_rates={"USD/AUD": "1.51"}, cfg=m.MatchConfig(bank_currency="USD"))
    assert rep.matches[0].match_type == "fx"
    assert rep.matches[0].difference == Decimal("-0.03")  # 100 / 1.51 = 66.2252 -> 66.23 expected


def test_negative_payout_and_internal_mismatch():
    lines = [m.PayoutLine("paypal", "W9", date(2026, 9, 1), "refund", "#1", Decimal("-30"), Decimal("0"), Decimal("-30"), "AUD")]
    rep = m.reconcile(lines, [], [], cfg=m.MatchConfig(bank_currency="AUD"),
                      declared_totals={"W9": Decimal("-25")})
    kinds = {e.kind for e in rep.exceptions}
    assert {"negative_payout", "provider_internal_mismatch"} <= kinds


def test_report_is_json_serialisable(report):
    import json
    json.dumps(report.to_dict())


# ----------------------------------------------------- summary & handlers

def test_fallback_summary_mentions_high_items_first(report):
    text = fallback_summary(report)
    assert "Payout reconciliation 2026-09" in text
    first_exc = text.split("Exceptions")[1].splitlines()[1]
    assert first_exc.startswith("- [HIGH]")


def test_llm_summary_uses_prompt_and_numbers(report):
    client = FakeClient([fake_text("**Payout reconciliation 2026-09: Needs attention: 4 issues**")])
    out = write_summary(report, client=client)
    assert out.startswith("**Payout reconciliation")
    call = client.calls[0]
    assert "month-end close assistant" in call["system"]
    assert "323.70" in call["messages"][0]["content"]
    assert summary_input(report).count('"severity": "high"') >= 3


def test_handlers_report_and_exceptions():
    rep = get_reconciliation_report("2026-09")
    assert rep["exception_count"] == len(list_exceptions("2026-09")["exceptions"])
    highs = list_exceptions("2026-09", severity="high")["exceptions"]
    assert {e["kind"] for e in highs} == {"bank_amount_mismatch", "accounting_mismatch", "unmatched_bank_line"}
