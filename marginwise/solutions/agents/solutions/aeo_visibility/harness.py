"""AEO visibility harness: ask assistants buying questions, parse, score."""

from __future__ import annotations

import string
from pathlib import Path

from core.fixtures import load_json

from .parser import mentions_to_dicts, parse_answer, share_of_voice

FIXTURES = Path(__file__).parent / "fixtures"
QUESTION_SETS = load_json(FIXTURES / "questions.json")


def build_questions(set_name: str, language: str = "en", **values: str) -> list[dict]:
    """Fill a template set. Raises KeyError if a placeholder has no value."""
    templates = QUESTION_SETS[set_name][language]
    out = []
    for t in templates:
        fields = {f for _, f, _, _ in string.Formatter().parse(t["template"]) if f}
        missing = fields - set(values)
        if missing:
            raise KeyError(f"template {t['id']} needs {sorted(missing)}")
        out.append({"id": t["id"], "question": t["template"].format(**values)})
    return out


def run(questions: list[dict], adapters: list, brands: list[dict], market: dict | None = None,
        repeats: int = 1) -> dict:
    """Ask every question to every adapter (optionally several times: answers vary run to run)."""
    results, errors = [], []
    for adapter in adapters:
        for q in questions:
            for _ in range(repeats):
                try:
                    answer = adapter.ask(q["question"], market, question_id=q["id"])
                except NotImplementedError as exc:
                    errors.append({"assistant": adapter.name, "error": str(exc)})
                    break
                results.append({"assistant": adapter.name, "question_id": q["id"], "question": q["question"],
                                "answer": answer, "mentions": mentions_to_dicts(parse_answer(answer, brands))})
    return {"results": results, "errors": errors, "score": share_of_voice(results, brands)}
