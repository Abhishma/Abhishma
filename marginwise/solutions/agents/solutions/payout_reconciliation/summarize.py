"""Month-end exceptions summary: the only LLM step in payout reconciliation.

The matcher produces all numbers. The model only writes prose around them,
and is instructed never to compute new figures. A deterministic fallback
summary is produced when no client is passed (offline runs, or as a check).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core import config
from core.llm import complete

from .matcher import ReconciliationReport

PROMPT = (Path(__file__).parent / "prompt.md").read_text(encoding="utf-8")

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def summary_input(report: ReconciliationReport) -> str:
    data = report.to_dict()
    data["exceptions"] = sorted(data["exceptions"], key=lambda e: SEVERITY_ORDER.get(e["severity"], 9))
    return ("Write the month-end exceptions summary for this reconciliation report. "
            "Use only the figures in the JSON.\n\n```json\n" + json.dumps(data, indent=2) + "\n```")


def write_summary(report: ReconciliationReport, client: Any = None, model: str = config.DEFAULT_MODEL) -> str:
    if client is None:
        return fallback_summary(report)
    return complete(client, PROMPT, summary_input(report), model=model, max_tokens=3000)


def fallback_summary(report: ReconciliationReport) -> str:
    d = report.to_dict()
    lines = [f"Payout reconciliation {d['period']} (bank currency {d['bank_currency']})", ""]
    lines.append("Totals by provider:")
    for row in d["totals"].values():
        lines.append(
            f"- {row['provider']} ({row['currency']}): {row['matched']}/{row['payouts']} payouts matched; "
            f"sales {row['gross_sales']}, refunds {row['refunds']}, chargebacks {row['chargebacks']}, "
            f"fees {row['fees']} ({row['effective_fee_rate_pct']}%), net {row['net']}")
    lines.append("")
    exc = sorted(d["exceptions"], key=lambda e: SEVERITY_ORDER.get(e["severity"], 9))
    lines.append(f"Exceptions ({len(exc)}):")
    for e in exc:
        lines.append(f"- [{e['severity'].upper()}] {e['kind']} {e['provider']} {e['reference']}: "
                     f"{e['amount']} {e['currency']} - {e['detail']}")
    return "\n".join(lines)
