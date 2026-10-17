"""Deterministic landed-cost calculator for US and Canada imports.

All rates are INPUTS. This module does not know tariff schedules; the human
reviewer supplies the duty rate for the confirmed national tariff line (US
HTSUS 10-digit, Canada 10-digit customs tariff) and any surcharge in force
(for example Section 301 / IEEPA tariffs in the US, or Canadian surtaxes /
counter-tariffs). Rates change often: always confirm the rate on the entry date.

Valuation:
  - US and Canada value goods for duty on a transaction / FOB-style basis that
    generally excludes international freight and insurance; set
    valuation_basis="CIF" for destinations that include them (e.g. EU, AU).
  - Canada GST (or HST in participating provinces) is charged on value for
    duty + duties + surtaxes.

US fees (defaults are parameters, verify with CBP for the entry date):
  - Merchandise Processing Fee (formal entries): 0.3464% ad valorem with a
    minimum and maximum that CBP adjusts each fiscal year
  - Harbor Maintenance Fee: 0.125% for ocean shipments
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _d(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def _q(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass
class USFees:
    mpf_rate_pct: Decimal = Decimal("0.3464")
    mpf_min: Decimal = Decimal("33.58")  # verify current fiscal-year figure with CBP
    mpf_max: Decimal = Decimal("651.50")  # verify current fiscal-year figure with CBP
    formal_entry_threshold: Decimal = Decimal("2500")
    informal_mpf_flat: Decimal = Decimal("0")  # set per broker/carrier for informal entries
    hmf_rate_pct: Decimal = Decimal("0.125")


def calculate_landed_cost(
    goods_value,
    fx_rate,
    duty_rate_pct,
    destination: str = "US",
    tariff_surcharge_pct=0,
    freight=0,
    insurance=0,
    quantity: int = 1,
    mode: str = "air",
    valuation_basis: str | None = None,
    import_tax_pct=None,
    broker_fee=0,
    goods_currency: str = "",
    import_currency: str = "",
    us_fees: USFees | None = None,
) -> dict:
    """Return a full landed-cost breakdown in the import currency.

    goods_value, freight, insurance: in goods currency (e.g. AUD, CNY)
    fx_rate: units of import currency per 1 unit of goods currency
    duty_rate_pct / tariff_surcharge_pct / import_tax_pct: percentages (e.g. 12 = 12%)
    broker_fee: in import currency
    """
    dest = destination.upper()
    if dest not in ("US", "CA", "OTHER"):
        raise ValueError("destination must be US, CA or OTHER")
    if quantity < 1:
        raise ValueError("quantity must be >= 1")
    fx = _d(fx_rate)
    if fx <= 0:
        raise ValueError("fx_rate must be positive")
    for name, v in (("goods_value", goods_value), ("freight", freight), ("insurance", insurance),
                    ("duty_rate_pct", duty_rate_pct), ("tariff_surcharge_pct", tariff_surcharge_pct)):
        if _d(v) < 0:
            raise ValueError(f"{name} cannot be negative")

    basis = (valuation_basis or ("FOB" if dest in ("US", "CA") else "CIF")).upper()
    goods = _q(_d(goods_value) * fx)
    freight_c = _q(_d(freight) * fx)
    insurance_c = _q(_d(insurance) * fx)
    customs_value = goods + (freight_c + insurance_c if basis == "CIF" else Decimal("0"))

    duty = _q(customs_value * _d(duty_rate_pct) / 100)
    surcharge = _q(customs_value * _d(tariff_surcharge_pct) / 100)

    mpf = hmf = _q(Decimal("0"))
    if dest == "US":
        fees = us_fees or USFees()
        if customs_value > fees.formal_entry_threshold:
            mpf = _q(min(max(customs_value * fees.mpf_rate_pct / 100, fees.mpf_min), fees.mpf_max))
        else:
            mpf = _q(fees.informal_mpf_flat)
        if mode == "ocean":
            hmf = _q(customs_value * fees.hmf_rate_pct / 100)

    if import_tax_pct is None:
        import_tax_pct = 5 if dest == "CA" else 0  # CA GST default; pass HST rate for HST provinces
    tax_base = customs_value + duty + surcharge
    import_tax = _q(tax_base * _d(import_tax_pct) / 100)

    broker = _q(_d(broker_fee))
    total = goods + freight_c + insurance_c + duty + surcharge + mpf + hmf + import_tax + broker
    return {
        "destination": dest,
        "goods_currency": goods_currency,
        "import_currency": import_currency or ("USD" if dest == "US" else "CAD" if dest == "CA" else ""),
        "valuation_basis": basis,
        "fx_rate": str(fx),
        "goods_value": str(goods),
        "freight": str(freight_c),
        "insurance": str(insurance_c),
        "customs_value": str(customs_value),
        "duty_rate_pct": str(_d(duty_rate_pct)),
        "duty": str(duty),
        "tariff_surcharge_pct": str(_d(tariff_surcharge_pct)),
        "tariff_surcharge": str(surcharge),
        "mpf": str(mpf),
        "hmf": str(hmf),
        "import_tax_pct": str(_d(import_tax_pct)),
        "import_tax": str(import_tax),
        "broker_fee": str(broker),
        "landed_total": str(_q(total)),
        "landed_per_unit": str(_q(total / quantity)),
        "duties_and_taxes": str(_q(duty + surcharge + mpf + hmf + import_tax)),
        "note": "Rates are inputs; confirm the national tariff line and rates on the entry date.",
    }
