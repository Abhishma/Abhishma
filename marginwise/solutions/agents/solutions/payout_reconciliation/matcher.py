"""Deterministic payout reconciliation (pure Python, no LLM).

Pipeline:
  1. parse provider exports (Shopify Payments, PayPal, Afterpay, Klarna, Stripe)
     into normalised PayoutLine records
  2. group lines into Payouts (gross sales, refunds, chargebacks, fees, net)
  3. match each payout to one bank statement line (amount, date window,
     provider keyword / reference, FX tolerance for cross-currency payouts)
  4. match each payout to its accounting clearing entry (Xero/MYOB/QuickBooks)
  5. emit exceptions: unmatched items, amount mismatches, chargebacks,
     FX variance, provider internal mismatches, pending items

All money is Decimal. Sign convention for a line:
  gross  > 0 for charges, < 0 for refunds and chargebacks
  fee    >= 0 is a cost to the merchant (a fee refund is negative)
  net    = gross - fee
"""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Iterable

CENT = Decimal("0.01")
ZERO = Decimal("0")

PROVIDER_KEYWORDS = {
    "shopify": ("SHOPIFY",),
    "paypal": ("PAYPAL",),
    "afterpay": ("AFTERPAY", "CLEARPAY"),
    "klarna": ("KLARNA",),
    "stripe": ("STRIPE",),
}


def D(value: str | float | int | Decimal | None) -> Decimal:
    if value is None or value == "":
        return ZERO
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value).replace(",", "").strip())


def q(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _date(value: str) -> date:
    return date.fromisoformat(value.strip()[:10])


# ---------------------------------------------------------------- data types


@dataclass
class PayoutLine:
    provider: str
    payout_id: str
    payout_date: date
    kind: str  # charge | refund | chargeback | fee | adjustment
    order_id: str
    gross: Decimal
    fee: Decimal
    net: Decimal
    currency: str
    presentment_amount: Decimal | None = None
    presentment_currency: str | None = None


@dataclass
class Payout:
    provider: str
    payout_id: str
    payout_date: date
    currency: str
    lines: list[PayoutLine] = field(default_factory=list)
    declared_total: Decimal | None = None  # provider's stated payout amount, when given
    status: str = "paid"

    def _sum(self, attr: str, kinds: Iterable[str] | None = None) -> Decimal:
        return sum((getattr(l, attr) for l in self.lines if kinds is None or l.kind in kinds), ZERO)

    @property
    def gross_sales(self) -> Decimal:
        return self._sum("gross", ["charge"])

    @property
    def refunds(self) -> Decimal:
        return self._sum("gross", ["refund"])

    @property
    def chargebacks(self) -> Decimal:
        return self._sum("gross", ["chargeback"])

    @property
    def adjustments(self) -> Decimal:
        return self._sum("gross", ["adjustment"])

    @property
    def fees(self) -> Decimal:
        return self._sum("fee")

    @property
    def net(self) -> Decimal:
        return self._sum("net")


@dataclass
class BankLine:
    line_id: str
    date: date
    description: str
    amount: Decimal
    currency: str
    reference: str = ""


@dataclass
class AccountingEntry:
    entry_id: str
    date: date
    reference: str
    account: str
    amount: Decimal
    currency: str
    source: str = ""


@dataclass
class Match:
    provider: str
    payout_id: str
    payout_net: Decimal
    payout_currency: str
    bank_line_id: str | None
    bank_amount: Decimal | None
    bank_currency: str | None
    match_type: str  # exact | fx | amount_mismatch | none
    difference: Decimal = ZERO  # bank - expected (in bank currency)
    fx_rate: Decimal | None = None
    days_to_bank: int | None = None
    accounting_entry_id: str | None = None
    accounting_difference: Decimal | None = None


@dataclass
class ReconException:
    kind: str
    severity: str  # low | medium | high
    provider: str
    reference: str
    amount: Decimal
    currency: str
    detail: str


@dataclass
class ReconciliationReport:
    period: str
    bank_currency: str
    payouts: list[Payout]
    matches: list[Match]
    exceptions: list[ReconException]
    unmatched_bank_lines: list[BankLine]
    unmatched_accounting_entries: list[AccountingEntry]
    ignored_bank_lines: int
    totals: dict

    def to_dict(self) -> dict:
        def conv(v):
            if isinstance(v, Decimal):
                return str(v)
            if isinstance(v, date):
                return v.isoformat()
            if isinstance(v, dict):
                return {k: conv(x) for k, x in v.items()}
            if isinstance(v, list):
                return [conv(x) for x in v]
            return v

        return conv({
            "period": self.period,
            "bank_currency": self.bank_currency,
            "totals": self.totals,
            "matches": [asdict(m) for m in self.matches],
            "exceptions": [asdict(e) for e in self.exceptions],
            "unmatched_bank_lines": [asdict(b) for b in self.unmatched_bank_lines],
            "unmatched_accounting_entries": [asdict(a) for a in self.unmatched_accounting_entries],
            "ignored_bank_lines": self.ignored_bank_lines,
            "payout_count": len(self.payouts),
        })


# ------------------------------------------------------------------- parsers


def _rows(source: str | Path) -> list[dict[str, str]]:
    """Accept a path or raw CSV text."""
    text = Path(source).read_text(encoding="utf-8-sig") if isinstance(source, Path) or (
        isinstance(source, str) and "\n" not in source and Path(source).exists()) else str(source)
    return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(io.StringIO(text))]


def parse_shopify(source) -> list[PayoutLine]:
    """Shopify Payments payout transactions export."""
    kinds = {"charge": "charge", "refund": "refund", "chargeback": "chargeback",
             "chargeback won": "adjustment", "adjustment": "adjustment"}
    out = []
    for r in _rows(source):
        out.append(PayoutLine(
            provider="shopify", payout_id=r["Payout ID"], payout_date=_date(r["Payout Date"]),
            kind=kinds.get(r["Type"].lower(), "adjustment"), order_id=r["Order"],
            gross=D(r["Amount"]), fee=D(r["Fee"]), net=D(r["Net"]), currency=r["Currency"].upper(),
        ))
    return out


def parse_paypal(source) -> tuple[list[PayoutLine], dict[str, Decimal], list[dict]]:
    """PayPal activity download. Transactions belong to the next General Withdrawal.

    Returns (lines, declared withdrawal totals by id, pending rows excluded).
    """
    kinds = {"express checkout payment": "charge", "website payment": "charge",
             "mobile payment": "charge", "payment refund": "refund", "chargeback": "chargeback",
             "chargeback reversal": "adjustment", "hold on balance for dispute investigation": "adjustment"}
    rows = sorted(_rows(source), key=lambda r: r["Date"])
    pending_rows, buffer, lines, declared = [], [], [], {}
    for r in rows:
        if r["Status"].lower() != "completed":
            pending_rows.append(r)
            continue
        if r["Type"].lower() == "general withdrawal":
            wid, wdate = r["Transaction ID"], _date(r["Date"])
            declared[wid] = -D(r["Gross"])
            for b in buffer:
                fee = -D(b["Fee"])  # PayPal shows fees as negative numbers
                lines.append(PayoutLine(
                    provider="paypal", payout_id=wid, payout_date=wdate,
                    kind=kinds.get(b["Type"].lower(), "adjustment"), order_id=b["Invoice Number"],
                    gross=D(b["Gross"]), fee=fee, net=D(b["Net"]), currency=b["Currency"].upper(),
                ))
            buffer = []
        else:
            buffer.append(r)
    # Completed rows after the last withdrawal stay in the PayPal balance (not paid out yet).
    pending_rows.extend(buffer)
    return lines, declared, pending_rows


def parse_afterpay(source) -> list[PayoutLine]:
    out = []
    for r in _rows(source):
        kind = "refund" if r["Type"].lower() == "refund" else "charge"
        out.append(PayoutLine(
            provider="afterpay", payout_id=r["Settlement ID"], payout_date=_date(r["Settlement Date"]),
            kind=kind, order_id=r["Order ID"], gross=D(r["Order Amount"]), fee=D(r["Merchant Fee"]),
            net=D(r["Net Amount"]), currency=r["Currency"].upper(),
        ))
    return out


def parse_klarna(source) -> list[PayoutLine]:
    """Klarna settlement report: one signed amount per row; fees are separate rows."""
    out = []
    for r in _rows(source):
        t, amt = r["type"].upper(), D(r["amount"])
        if t in ("FEE", "FEE_CORRECTION"):
            kind, gross, fee = "fee", ZERO, -amt
        elif t == "RETURN":
            kind, gross, fee = "refund", amt, ZERO
        elif t == "SALE":
            kind, gross, fee = "charge", amt, ZERO
        elif t == "CHARGEBACK":
            kind, gross, fee = "chargeback", amt, ZERO
        else:
            kind, gross, fee = "adjustment", amt, ZERO
        out.append(PayoutLine(
            provider="klarna", payout_id=r["payment_reference"], payout_date=_date(r["payout_date"]),
            kind=kind, order_id=r["order_id"], gross=gross, fee=fee, net=gross - fee,
            currency=r["currency"].upper(),
        ))
    return out


def parse_stripe(source) -> list[PayoutLine]:
    """Stripe 'Payout reconciliation' itemised report."""
    kinds = {"charge": "charge", "refund": "refund", "dispute": "chargeback",
             "dispute_reversal": "adjustment", "fee": "fee", "other_adjustment": "adjustment"}
    out = []
    for r in _rows(source):
        out.append(PayoutLine(
            provider="stripe", payout_id=r["automatic_payout_id"],
            payout_date=_date(r["automatic_payout_effective_at"]),
            kind=kinds.get(r["reporting_category"].lower(), "adjustment"), order_id=r.get("order_id", ""),
            gross=D(r["gross"]), fee=D(r["fee"]), net=D(r["net"]), currency=r["currency"].upper(),
            presentment_amount=D(r["customer_facing_amount"]) if r.get("customer_facing_amount") else None,
            presentment_currency=(r.get("customer_facing_currency") or "").upper() or None,
        ))
    return out


def parse_bank(source) -> list[BankLine]:
    return [BankLine(line_id=f"BANK-{i:04d}", date=_date(r["Date"]), description=r["Description"],
                     amount=D(r["Amount"]), currency=r["Currency"].upper(), reference=r.get("Reference", ""))
            for i, r in enumerate(_rows(source), start=1)]


def parse_accounting(source) -> list[AccountingEntry]:
    return [AccountingEntry(entry_id=f"ACC-{i:04d}", date=_date(r["Date"]), reference=r["Reference"],
                            account=r["Account"], amount=D(r["Amount"]), currency=r["Currency"].upper(),
                            source=r.get("Source", ""))
            for i, r in enumerate(_rows(source), start=1)]


# ------------------------------------------------------------------ grouping


def group_payouts(lines: list[PayoutLine], declared: dict[str, Decimal] | None = None,
                  statuses: dict[str, str] | None = None) -> list[Payout]:
    groups: dict[tuple[str, str], Payout] = {}
    for l in lines:
        key = (l.provider, l.payout_id)
        if key not in groups:
            groups[key] = Payout(provider=l.provider, payout_id=l.payout_id,
                                 payout_date=l.payout_date, currency=l.currency)
        groups[key].lines.append(l)
    for p in groups.values():
        if declared and p.payout_id in declared:
            p.declared_total = declared[p.payout_id]
        if statuses and p.payout_id in statuses:
            p.status = statuses[p.payout_id]
    return sorted(groups.values(), key=lambda p: (p.payout_date, p.provider, p.payout_id))


# ------------------------------------------------------------------ matching


@dataclass
class MatchConfig:
    bank_currency: str = "AUD"
    max_days_to_bank: int = 7
    days_before_allowed: int = 1
    fx_tolerance_pct: Decimal = Decimal("3.0")  # cross-currency acceptance band
    fx_flag_pct: Decimal = Decimal("0.75")  # report FX variance above this
    amount_tolerance: Decimal = CENT
    period_end: date | None = None
    in_transit_days: int = 3


def _keyword_hit(provider: str, line: BankLine) -> bool:
    text = f"{line.description} {line.reference}".upper()
    return any(k in text for k in PROVIDER_KEYWORDS.get(provider, ()))


def _rate(fx_rates: dict[str, Decimal], src: str, dst: str) -> Decimal | None:
    if src == dst:
        return Decimal("1")
    if f"{src}/{dst}" in fx_rates:
        return D(fx_rates[f"{src}/{dst}"])
    if f"{dst}/{src}" in fx_rates:
        return Decimal("1") / D(fx_rates[f"{dst}/{src}"])
    return None


def match_bank(payouts: list[Payout], bank: list[BankLine], fx_rates: dict, cfg: MatchConfig) -> tuple[list[Match], list[BankLine]]:
    """One-to-one greedy matching by best score per payout (largest payouts first)."""
    used: set[str] = set()
    matches: list[Match] = []
    for p in sorted(payouts, key=lambda x: (-abs(x.net), x.payout_date)):
        best, best_score, best_info = None, None, None
        rate = _rate(fx_rates, p.currency, cfg.bank_currency)
        for b in bank:
            if b.line_id in used:
                continue
            delta_days = (b.date - p.payout_date).days
            if delta_days < -cfg.days_before_allowed or delta_days > cfg.max_days_to_bank:
                continue
            ref_hit = bool(b.reference) and b.reference.upper() == p.payout_id.upper()
            kw = _keyword_hit(p.provider, b)
            if not (kw or ref_hit):
                continue
            if b.currency == p.currency:
                expected, mtype = p.net, None
                if abs(b.amount - expected) <= cfg.amount_tolerance:
                    mtype = "exact"
            elif rate is not None:
                expected = q(p.net * rate)
                pct = abs(b.amount - expected) / abs(expected) * 100 if expected else Decimal("100")
                mtype = "fx" if pct <= cfg.fx_tolerance_pct else None
            else:
                continue
            if mtype is None:
                # Same provider and date window but wrong amount: candidate mismatch only
                # when the reference confirms it or it is the only same-provider line.
                mtype = "amount_mismatch" if ref_hit else "weak"
            score = {"exact": 100, "fx": 80, "amount_mismatch": 40, "weak": 10}[mtype] + (15 if ref_hit else 0) - delta_days
            if best_score is None or score > best_score:
                best, best_score, best_info = b, score, (mtype, expected, delta_days)
        if best is not None and best_info[0] != "weak":
            mtype, expected, delta_days = best_info
            used.add(best.line_id)
            matches.append(Match(
                provider=p.provider, payout_id=p.payout_id, payout_net=p.net, payout_currency=p.currency,
                bank_line_id=best.line_id, bank_amount=best.amount, bank_currency=best.currency,
                match_type=mtype, difference=q(best.amount - expected),
                fx_rate=rate if p.currency != best.currency else None, days_to_bank=delta_days,
            ))
        else:
            matches.append(Match(provider=p.provider, payout_id=p.payout_id, payout_net=p.net,
                                 payout_currency=p.currency, bank_line_id=None, bank_amount=None,
                                 bank_currency=None, match_type="none"))
    unmatched = [b for b in bank if b.line_id not in used]
    return matches, unmatched


def match_accounting(payouts: list[Payout], entries: list[AccountingEntry], matches: list[Match]) -> list[AccountingEntry]:
    """Match clearing entries by payout reference (exact, case-insensitive)."""
    by_ref: dict[str, list[AccountingEntry]] = defaultdict(list)
    for e in entries:
        by_ref[e.reference.upper()].append(e)
    used: set[str] = set()
    mindex = {(m.provider, m.payout_id): m for m in matches}
    for p in payouts:
        cands = [e for e in by_ref.get(p.payout_id.upper(), []) if e.entry_id not in used]
        if not cands:
            continue
        e = min(cands, key=lambda x: abs(x.amount - p.net))
        used.add(e.entry_id)
        m = mindex[(p.provider, p.payout_id)]
        m.accounting_entry_id = e.entry_id
        m.accounting_difference = q(e.amount - p.net) if e.currency == p.currency else None
    return [e for e in entries if e.entry_id not in used]


# ------------------------------------------------------------- orchestration


def reconcile(
    payout_lines: list[PayoutLine],
    bank: list[BankLine],
    accounting: list[AccountingEntry],
    fx_rates: dict | None = None,
    cfg: MatchConfig | None = None,
    declared_totals: dict[str, Decimal] | None = None,
    payout_statuses: dict[str, str] | None = None,
    pending_provider_rows: list[dict] | None = None,
    period: str = "",
) -> ReconciliationReport:
    cfg = cfg or MatchConfig()
    fx_rates = fx_rates or {}
    payouts = group_payouts(payout_lines, declared_totals, payout_statuses)
    matches, unmatched_bank = match_bank(payouts, bank, fx_rates, cfg)
    unmatched_acc = match_accounting(payouts, accounting, matches)
    pmap = {(p.provider, p.payout_id): p for p in payouts}
    exceptions: list[ReconException] = []

    def add(kind, sev, provider, ref, amount, cur, detail):
        exceptions.append(ReconException(kind, sev, provider, ref, q(D(amount)), cur, detail))

    for m in matches:
        p = pmap[(m.provider, m.payout_id)]
        if p.declared_total is not None and abs(p.declared_total - p.net) > cfg.amount_tolerance:
            add("provider_internal_mismatch", "high", p.provider, p.payout_id, p.declared_total - p.net,
                p.currency, f"provider states {p.declared_total} but lines sum to {p.net}")
        if p.net < 0:
            add("negative_payout", "medium", p.provider, p.payout_id, p.net, p.currency,
                "payout is a debit (refunds/chargebacks exceeded sales)")
        if m.match_type == "none":
            in_transit = p.status == "in_transit" or (
                cfg.period_end is not None and (cfg.period_end - p.payout_date).days <= cfg.in_transit_days)
            add("unmatched_payout", "low" if in_transit else "high", p.provider, p.payout_id, p.net, p.currency,
                "in transit at period end; expect in next statement" if in_transit else "no bank deposit found")
        elif m.match_type == "amount_mismatch":
            add("bank_amount_mismatch", "high", p.provider, p.payout_id, m.difference, m.bank_currency or p.currency,
                f"bank received {m.bank_amount} vs payout {p.net}")
        elif m.match_type == "fx":
            pct = abs(m.difference) / abs(m.bank_amount) * 100 if m.bank_amount else ZERO
            if pct >= cfg.fx_flag_pct:
                add("fx_variance", "medium", p.provider, p.payout_id, m.difference, m.bank_currency,
                    f"{p.net} {p.currency} at reference {q(m.fx_rate) if m.fx_rate else '?'} vs bank {m.bank_amount} "
                    f"({pct.quantize(Decimal('0.01'))}%)")
        if m.accounting_entry_id is None:
            add("missing_in_accounting", "low" if p.status == "in_transit" else "medium", p.provider,
                p.payout_id, p.net, p.currency, "no clearing entry references this payout")
        elif m.accounting_difference not in (None, ZERO) and abs(m.accounting_difference) > cfg.amount_tolerance:
            add("accounting_mismatch", "high", p.provider, p.payout_id, m.accounting_difference, p.currency,
                "clearing entry differs from payout net (often an unposted fee, refund or chargeback)")
        for l in p.lines:
            if l.kind == "chargeback":
                add("chargeback", "medium", p.provider, l.order_id or p.payout_id, l.gross, l.currency,
                    f"chargeback in payout {p.payout_id}, fee {l.fee}")

    ignored = 0
    leftover_bank = []
    for b in unmatched_bank:
        provider = next((pr for pr in PROVIDER_KEYWORDS if _keyword_hit(pr, b)), None)
        if provider is None:
            ignored += 1  # rent, transfers etc. are out of scope
            continue
        leftover_bank.append(b)
        add("unmatched_bank_line", "high", provider, b.line_id, b.amount, b.currency,
            f"{b.date} '{b.description}' has no provider payout")
    for e in unmatched_acc:
        add("accounting_entry_without_payout", "medium", "accounting", e.reference, e.amount, e.currency,
            f"{e.account} entry {e.date} has no matching provider payout")
    for r in pending_provider_rows or []:
        add("pending_provider_balance", "low", "paypal", r.get("Transaction ID", ""), D(r.get("Net")),
            r.get("Currency", ""), f"{r.get('Status')} {r.get('Type')} not yet withdrawn")

    totals = _totals(payouts, matches)
    return ReconciliationReport(
        period=period, bank_currency=cfg.bank_currency, payouts=payouts, matches=matches,
        exceptions=exceptions, unmatched_bank_lines=leftover_bank,
        unmatched_accounting_entries=unmatched_acc, ignored_bank_lines=ignored, totals=totals,
    )


def _totals(payouts: list[Payout], matches: list[Match]) -> dict:
    t: dict[str, dict] = {}
    mindex = {(m.provider, m.payout_id): m for m in matches}
    for p in payouts:
        key = f"{p.provider}:{p.currency}"
        row = t.setdefault(key, {"provider": p.provider, "currency": p.currency, "payouts": 0, "matched": 0,
                                 "gross_sales": ZERO, "refunds": ZERO, "chargebacks": ZERO, "adjustments": ZERO,
                                 "fees": ZERO, "net": ZERO, "fx_variance_bank_ccy": ZERO})
        m = mindex[(p.provider, p.payout_id)]
        row["payouts"] += 1
        row["matched"] += m.match_type in ("exact", "fx")
        for f in ("gross_sales", "refunds", "chargebacks", "adjustments", "fees", "net"):
            row[f] += getattr(p, f)
        if m.match_type == "fx":
            row["fx_variance_bank_ccy"] += m.difference
    for row in t.values():
        row["effective_fee_rate_pct"] = (
            (row["fees"] / row["gross_sales"] * 100).quantize(Decimal("0.01")) if row["gross_sales"] else ZERO)
    return t


def reconcile_files(folder: str | Path, bank_currency: str = "AUD", period: str = "",
                    period_end: date | None = None) -> ReconciliationReport:
    """Convenience loader for a folder laid out like fixtures/."""
    import json

    folder = Path(folder)
    lines: list[PayoutLine] = []
    declared: dict[str, Decimal] = {}
    pending: list[dict] = []
    statuses: dict[str, str] = {}
    if (folder / "shopify_payouts.csv").exists():
        lines += parse_shopify(folder / "shopify_payouts.csv")
        for r in _rows(folder / "shopify_payouts.csv"):
            if r["Payout Status"].lower() != "paid":
                statuses[r["Payout ID"]] = r["Payout Status"].lower()
    if (folder / "paypal_activity.csv").exists():
        pl, declared, pending = parse_paypal(folder / "paypal_activity.csv")
        lines += pl
    if (folder / "afterpay_settlements.csv").exists():
        lines += parse_afterpay(folder / "afterpay_settlements.csv")
    if (folder / "klarna_settlements.csv").exists():
        lines += parse_klarna(folder / "klarna_settlements.csv")
    if (folder / "stripe_payout_reconciliation.csv").exists():
        lines += parse_stripe(folder / "stripe_payout_reconciliation.csv")
    fx = json.loads((folder / "fx_rates.json").read_text()) if (folder / "fx_rates.json").exists() else {}
    return reconcile(
        lines, parse_bank(folder / "bank_statement.csv"), parse_accounting(folder / "accounting_entries.csv"),
        fx_rates=fx, cfg=MatchConfig(bank_currency=bank_currency, period_end=period_end),
        declared_totals=declared, payout_statuses=statuses, pending_provider_rows=pending, period=period,
    )
