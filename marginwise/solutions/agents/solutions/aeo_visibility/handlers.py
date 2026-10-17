"""Handlers for the AEO visibility analyst agent.

The harness (harness.py) does the measuring; these tools let the analyst agent
run a check and read the scores, then write the client report.

TODO(adapters): replace FixtureAdapter with AnthropicAdapter / OpenAIAdapter /
PerplexityAdapter in production, store runs in a database (Postgres, BigQuery)
to trend share of voice month over month.
"""

from __future__ import annotations

from pathlib import Path

from core.fixtures import load_json

from .adapters import FixtureAdapter
from .harness import QUESTION_SETS, build_questions, run
from .parser import share_of_voice

FIXTURES = Path(__file__).parent / "fixtures"
BRANDS = load_json(FIXTURES / "brands.json")
STATE: dict[str, dict] = {"runs": {}}


def reset_state() -> None:
    STATE["runs"].clear()


def list_question_sets() -> dict:
    return {name: {lang: [t["template"] for t in ts] for lang, ts in langs.items()}
            for name, langs in QUESTION_SETS.items() if not name.startswith("_")}


def run_visibility_check(set_name: str, values: dict, language: str = "en",
                         assistants: list | None = None) -> dict:
    questions = build_questions(set_name, language, **values)
    names = assistants or ["anthropic", "openai", "perplexity"]
    adapters = [FixtureAdapter(n) for n in names]
    # Fixture answers exist only for some question ids; skip empty answers.
    out = run(questions, adapters, BRANDS["brands"], market=BRANDS["market"])
    out["results"] = [r for r in out["results"] if r["answer"]]
    out["score"] = share_of_voice(out["results"], BRANDS["brands"])
    run_id = f"AEO-{len(STATE['runs']) + 1:03d}"
    STATE["runs"][run_id] = out
    return {"run_id": run_id, "answers": len(out["results"]), "client": BRANDS["client"],
            "errors": out["errors"], "score": out["score"]}


def get_share_of_voice(run_id: str, include_answers: bool = False) -> dict:
    data = STATE["runs"].get(run_id)
    if data is None:
        return {"found": False, "error": f"run {run_id} not found"}
    result = {"found": True, "run_id": run_id, "client": BRANDS["client"], "score": data["score"]}
    if include_answers:
        result["answers"] = [{k: r[k] for k in ("assistant", "question", "mentions")} for r in data["results"]]
    return result


HANDLERS = {
    "list_question_sets": list_question_sets,
    "run_visibility_check": run_visibility_check,
    "get_share_of_voice": get_share_of_voice,
}
