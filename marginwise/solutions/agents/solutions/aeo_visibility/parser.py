"""Deterministic parsing of AI assistant answers into brand mentions and scores.

For each answer we find which tracked brands are named (canonical name or
alias, case-insensitive, word boundaries), their order of first appearance,
their rank if the answer is a numbered or bulleted list, whether the mention
reads as a recommendation or as negative, and a snippet.

Share of voice: each answer distributes points to the brands it names.
  - a brand in a list item gets 1 / list_rank
  - a brand mentioned only in prose gets 0.5 / position
  - a negative mention gets 0 points (still counted as a mention)
SoV(brand) = brand points / all points across all answers.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict, dataclass

_LIST_ITEM = re.compile(r"^\s*(?:(\d+)[.)]|[-*•])\s+(.*)$")
_POSITIVE = re.compile(r"\b(best|recommend(ed)?|top|popular|well[- ]regarded|top[- ]rated|go[- ]to|great|trusted|reliable)\b", re.I)
_NEGATIVE = re.compile(r"\b(avoid|complain(t|ts)?|poor|worst|not recommended|long wait|overpriced|scam|bad reviews?|issues)\b", re.I)


@dataclass
class Mention:
    brand: str
    position: int  # order of first appearance among tracked brands (1 = first)
    list_rank: int | None  # rank within the answer's list, if listed
    count: int
    sentiment: str  # positive | neutral | negative
    snippet: str


def _brand_regex(brand: dict) -> re.Pattern:
    names = sorted({brand["name"], *brand.get("aliases", [])}, key=len, reverse=True)
    alt = "|".join(re.escape(n) for n in names)
    return re.compile(rf"(?<![\w])({alt})(?![\w])", re.I)


def _sentence_around(text: str, idx: int) -> str:
    start = max(text.rfind(".", 0, idx), text.rfind("\n", 0, idx)) + 1
    ends = [i for i in (text.find(".", idx), text.find("\n", idx)) if i != -1]
    end = min(ends) if ends else len(text)
    return text[start:end].strip(" *-\n")


def parse_answer(text: str, brands: list[dict]) -> list[Mention]:
    text = text or ""
    found: list[tuple[int, dict, list[re.Match]]] = []
    for b in brands:
        matches = list(_brand_regex(b).finditer(text))
        if matches:
            found.append((matches[0].start(), b, matches))
    found.sort(key=lambda x: x[0])

    # List ranks: walk list items in order, assign each brand the first item it appears in.
    list_items = [m.group(2) for m in (_LIST_ITEM.match(line) for line in text.splitlines()) if m]
    ranks: dict[str, int] = {}
    for i, item in enumerate(list_items, start=1):
        for _, b, _ in found:
            if b["name"] not in ranks and _brand_regex(b).search(item):
                ranks[b["name"]] = i

    mentions = []
    for pos, (first, b, matches) in enumerate(found, start=1):
        snippet = _sentence_around(text, first)
        if _NEGATIVE.search(snippet):
            sentiment = "negative"
        elif b["name"] in ranks or _POSITIVE.search(snippet):
            sentiment = "positive"
        else:
            sentiment = "neutral"
        mentions.append(Mention(brand=b["name"], position=pos, list_rank=ranks.get(b["name"]),
                                count=len(matches), sentiment=sentiment, snippet=snippet[:200]))
    return mentions


def mention_points(m: Mention) -> float:
    if m.sentiment == "negative":
        return 0.0
    if m.list_rank:
        return 1.0 / m.list_rank
    return 0.5 / m.position


def share_of_voice(results: list[dict], brands: list[dict]) -> dict:
    """results: [{"assistant", "question_id", "mentions": [Mention or dict]}]."""
    points: dict[str, float] = defaultdict(float)
    answers_with: dict[str, int] = defaultdict(int)
    positions: dict[str, list[int]] = defaultdict(list)
    by_assistant: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    negatives: dict[str, int] = defaultdict(int)
    for r in results:
        for m in r["mentions"]:
            m = m if isinstance(m, Mention) else Mention(**m)
            p = mention_points(m)
            points[m.brand] += p
            by_assistant[r["assistant"]][m.brand] += p
            answers_with[m.brand] += 1
            positions[m.brand].append(m.position)
            negatives[m.brand] += m.sentiment == "negative"
    total = sum(points.values()) or 1.0
    n = len(results) or 1
    table = []
    for b in brands:
        name = b["name"]
        table.append({
            "brand": name,
            "share_of_voice_pct": round(100 * points[name] / total, 1),
            "mention_rate_pct": round(100 * answers_with[name] / n, 1),
            "avg_position": round(sum(positions[name]) / len(positions[name]), 2) if positions[name] else None,
            "negative_mentions": negatives[name],
            "points": round(points[name], 4),
        })
    table.sort(key=lambda x: -x["share_of_voice_pct"])
    assistants = {}
    for a, pts in by_assistant.items():
        t = sum(pts.values()) or 1.0
        assistants[a] = {b["name"]: round(100 * pts[b["name"]] / t, 1) for b in brands}
    return {"answers": len(results), "brands": table, "by_assistant": assistants}


def mentions_to_dicts(mentions: list[Mention]) -> list[dict]:
    return [asdict(m) for m in mentions]
