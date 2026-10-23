"""Deterministic pre-scan rules for marketing / product copy.

The LLM reviews these candidate hits in context (a hit is not automatically
a breach: "nachhaltig" can be fine with specific substantiation) and may add
findings the regexes miss. Regexes favour recall over precision.

Sources to check before relying on any rule (this is not legal advice):
  - EU Directive 2024/825 (Empowering Consumers for the Green Transition, "EmpCo"),
    applicable from 27 September 2026, implemented in Germany through the UWG
  - German Price Indication Ordinance (PAngV) section 11, price reductions
  - Meta Advertising Standards (health, weight loss, personal attributes,
    unrealistic outcomes)
  - Australian Consumer Law drip pricing prohibition (in force from 1 July 2025)
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

DISCLAIMER = (
    "Automated pre-screen only. This is not legal advice. Have a qualified "
    "lawyer review high-risk copy before publishing."
)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    category: str  # empco | pangv | meta_ads | au_drip_pricing
    markets: tuple[str, ...]
    pattern: re.Pattern
    risk: str  # high | medium | low
    rule: str
    rewrite_hint: str
    suppress_if: re.Pattern | None = None


def _r(p: str) -> re.Pattern:
    return re.compile(p, re.I | re.U)


RULES: list[Rule] = [
    Rule("EMPCO_CLIMATE_NEUTRAL", "empco", ("DE", "EU"),
         _r(r"\b(klima\s?neutral|klimapositiv|co(2|₂)[\s-]?neutral|climate[\s-]neutral|carbon[\s-]neutral|net[\s-]zero product)\w*"),
         "high",
         "Claims that a product has a neutral, reduced or positive climate impact based on offsetting are banned (EmpCo, UWG Annex).",
         "Remove the neutrality claim. State a specific, verifiable reduction for the product itself, e.g. 'Production uses 100% renewable electricity since 2025 (verified by ...)'. Offsetting may be described separately as a company contribution, not as a product property."),
    Rule("EMPCO_GENERIC_CLAIM", "empco", ("DE", "EU"),
         _r(r"\b(umweltfreundlich|umweltschonend|nachhaltig|ökologisch|oekologisch|klimafreundlich|grün(e|er|es)?\s(produkt|wahl)|eco[\s-]?friendly|environmentally[\s-]friendly|planet[\s-]friendly|sustainable|green choice|conscious choice)\w*"),
         "high",
         "Generic environmental claims are banned unless the trader can show recognised excellent environmental performance relevant to the claim (EmpCo).",
         "Replace with a specific, substantiated fact, e.g. 'Outer box made from 80% recycled cardboard' or 'Verpackung aus 80 % Recyclingkarton'."),
    Rule("EMPCO_SELF_LABEL", "empco", ("DE", "EU"),
         _r(r"\b((unser|eigene[sn]?|our own|our)\s+(öko|oeko|eco|green|nachhaltigkeits|sustainability)?[\s-]?(siegel|label|badge|seal|zertifikat|certified))"),
         "high",
         "Sustainability labels not based on a certification scheme or set up by public authorities are banned (EmpCo).",
         "Remove the self-made label, or replace it with a recognised third-party certification you actually hold (name the scheme and licence number)."),
    Rule("EMPCO_BIODEGRADABLE", "empco", ("DE", "EU"),
         _r(r"\b(biologisch abbaubar|biodegradable|kompostierbar|compostable|plastikfrei|plastic[\s-]free)\b"),
         "medium",
         "Environmental claims must be specific and verifiable; conditions (industrial vs home composting, which part of the product) must be stated.",
         "Specify the part and condition, e.g. 'Cup is certified industrially compostable (EN 13432); lid is recyclable PP'."),
    Rule("PANGV_PRICE_REDUCTION", "pangv", ("DE",),
         _r(r"(\bstatt\b|\bvorher\b|streichpreis|\breduziert\b|\bjetzt nur\b|\bsale\b|-\s?\d{1,2}\s?%|\d{1,2}\s?%\s?(rabatt|reduziert|off)|\bwas\s+€?\s?\d)"),
         "medium",
         "PAngV section 11: when announcing a price reduction, the lowest total price of the previous 30 days must be given as the reference price.",
         "Add the reference: 'Niedrigster Preis der letzten 30 Tage: 49,99 EUR' next to the reduced price, and use that price as the strike-through value. Label RRP comparisons clearly as 'UVP des Herstellers'.",
         suppress_if=_r(r"niedrigste[rn]?\s+(gesamt)?preis\s+(der\s+)?letzten\s+30\s+tage|lowest price (of|in) the (last|previous) 30 days")),
    Rule("META_UNREALISTIC_OUTCOME", "meta_ads", ("AU", "NZ", "US", "CA", "DE", "SA", "EU"),
         _r(r"(lose\s+\d+\s?(kg|kilos?|lbs?|pounds)\s+in\s+\d+\s+(days?|weeks?)|\d+\s?kg\s+in\s+\d+\s+(tagen|wochen)|guaranteed (results|to work|weight loss)|garantiert\s+abnehmen|overnight results|miracle|wundermittel|100\s?% (effective|guaranteed)|cures?\b|heilt\b|get rich|earn \$?\d[\d,]*\s+(a|per)\s+(day|week)|melt (the )?fat)"),
         "high",
         "Meta Advertising Standards prohibit unrealistic or exaggerated health, weight-loss and financial outcomes and implied guarantees.",
         "Describe the product's realistic benefit without numbers-in-timeframe promises, e.g. 'Supports your training routine as part of a balanced diet'."),
    Rule("META_PERSONAL_ATTRIBUTES", "meta_ads", ("AU", "NZ", "US", "CA", "DE", "SA", "EU"),
         _r(r"\b(are you (overweight|fat|depressed|in debt|diabetic|struggling with)|do you (have|suffer from) (diabetes|acne|anxiety|depression|debt)|sind sie (übergewichtig|uebergewichtig|depressiv)|other (fat|overweight) people)"),
         "medium",
         "Meta ads must not assert or imply personal attributes (health, financial status, etc.) of the person viewing the ad.",
         "Speak about the product, not the viewer: 'Our plan offers dietitian-designed meals' instead of 'Are you overweight?'."),
    Rule("AU_DRIP_PRICING", "au_drip_pricing", ("AU",),
         _r(r"(\+\s?\$?\d*\s?(booking|service|processing|admin|handling|card|cleaning|facility)\s+fees?|plus\s+(a\s+)?(booking|service|processing|admin|handling|facility)\s+fee|fees? (apply|added|calculated) at checkout|excl(udes|uding|\.)?\s+(booking|service|mandatory|processing)\s+fees?|from\s+\$\d[\d,.]*\s?\*)"),
         "high",
         "Australian Consumer Law drip pricing ban: mandatory fees must be included in the headline price shown upfront (optional extras and genuinely variable delivery costs may be shown separately, clearly).",
         "Show the total price including every mandatory fee, e.g. '$129 (includes booking fee)'. Remove 'fees apply at checkout' wording."),
    Rule("AU_ENVIRONMENTAL_CLAIM", "acl_environmental", ("AU",),
         _r(r"\b(eco[\s-]?friendly|environmentally[\s-]friendly|sustainable|green|carbon[\s-]neutral|planet[\s-]friendly|non[\s-]toxic)\b"),
         "medium",
         "ACCC guidance on environmental claims (Australian Consumer Law, misleading conduct): broad green claims must be specific and substantiated.",
         "Replace with the specific, evidenced attribute, e.g. 'Plant-based surfactants, readily biodegradable (OECD 301B)'."),
]


def _sentence(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start), text.rfind("!", 0, start)) + 1
    rights = [i for i in (text.find(".", end), text.find("\n", end), text.find("!", end)) if i != -1]
    right = min(rights) + 1 if rights else len(text)
    return text[left:right].strip()


def scan(text: str, markets: list[str] | None = None, channel: str = "") -> list[dict]:
    """Return candidate findings. markets filters rules; channel 'meta_ad' enables Meta rules."""
    markets = [m.upper() for m in (markets or ["DE", "EU", "AU", "US", "CA", "NZ"])]
    findings, seen = [], set()
    for rule in RULES:
        if rule.category == "meta_ads" and channel not in ("meta_ad", "all"):
            continue
        if not set(rule.markets) & set(markets):
            continue
        if rule.suppress_if and rule.suppress_if.search(text):
            continue
        for m in rule.pattern.finditer(text):
            key = (rule.rule_id, m.group(0).lower())
            if key in seen:
                continue
            seen.add(key)
            findings.append({
                "rule_id": rule.rule_id, "category": rule.category, "match": m.group(0),
                "quote": _sentence(text, m.start(), m.end()), "risk": rule.risk,
                "rule": rule.rule, "suggested_rewrite": rule.rewrite_hint,
            })
    return findings


def rules_summary() -> list[dict]:
    return [{k: v for k, v in asdict(r).items() if k not in ("pattern", "suppress_if")} for r in RULES]
