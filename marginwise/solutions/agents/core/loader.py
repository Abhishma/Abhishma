"""Load a solution: system prompt, tool schemas and Python handlers.

Layout of a solution directory (solutions/<name>/):

    prompt.md     system prompt (markdown)
    tools.json    {"requires_approval": [...], "tools": [<Anthropic tool schemas>]}
    handlers.py   defines HANDLERS: dict[str, callable]
    fixtures/     sample data used by the mock handlers

tools.json keeps the "tools" array in pure Anthropic tool-use format (name,
description, input_schema) so it can be passed to the Messages API unchanged.
Guardrail metadata lives next to it under "requires_approval".
"""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS_DIR = ROOT / "solutions"


@dataclass
class Solution:
    name: str
    system_prompt: str
    tools: list[dict]
    handlers: dict[str, Callable[..., Any]]
    requires_approval: set[str] = field(default_factory=set)
    path: Path | None = None

    @property
    def tool_names(self) -> list[str]:
        return [t["name"] for t in self.tools]


def list_solutions() -> list[str]:
    return sorted(
        p.name for p in SOLUTIONS_DIR.iterdir()
        if p.is_dir() and (p / "prompt.md").exists()
    )


def load_tools_file(path: Path) -> tuple[list[dict], set[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tools = data["tools"]
    approval = set(data.get("requires_approval", []))
    names = {t["name"] for t in tools}
    unknown = approval - names
    if unknown:
        raise ValueError(f"{path}: requires_approval lists unknown tools {sorted(unknown)}")
    for t in tools:
        for key in ("name", "description", "input_schema"):
            if key not in t:
                raise ValueError(f"{path}: tool {t.get('name')} is missing '{key}'")
    return tools, approval


def load_solution(name: str, prompt_file: str = "prompt.md") -> Solution:
    """Load solutions/<name>. Raises if handlers are missing for any tool."""
    sdir = SOLUTIONS_DIR / name
    prompt = (sdir / prompt_file).read_text(encoding="utf-8")
    tools, approval = load_tools_file(sdir / "tools.json")
    module = importlib.import_module(f"solutions.{name}.handlers")
    handlers: dict[str, Callable[..., Any]] = getattr(module, "HANDLERS", {})
    missing = [t["name"] for t in tools if t["name"] not in handlers]
    if missing:
        raise ValueError(f"solution {name}: no handler for tools {missing}")
    return Solution(
        name=name,
        system_prompt=prompt,
        tools=tools,
        handlers=handlers,
        requires_approval=approval,
        path=sdir,
    )
