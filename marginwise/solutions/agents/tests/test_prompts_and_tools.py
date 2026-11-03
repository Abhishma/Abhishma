"""Every solution's prompt.md and tools.json load, are consistent, and follow house rules."""

import json
import re
from pathlib import Path

import pytest

from core.loader import ROOT, SOLUTIONS_DIR, list_solutions, load_solution

EXPECTED = {
    "receptionist", "whatsapp_commerce", "support_wismo", "sync_exception", "payout_reconciliation",
    "po_to_order", "compliance_copy_auditor", "gpsr_extractor", "hs_classifier", "aeo_visibility",
    "lead_triage", "quote_builder",
}
REQUIRED_SECTIONS = [
    "Role", "Goals", "Tone", "Market and language rules", "Procedure", "Tool usage rules",
    "Escalation rules", "Limits and refusals", "Output format", "Examples",
]
BACKTICK_IDENT = re.compile(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F\U0001F1E6-\U0001F1FF]")


def test_all_solutions_present():
    assert set(list_solutions()) == EXPECTED


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_solution_loads_with_handlers(name):
    sol = load_solution(name)
    assert sol.system_prompt.strip()
    assert sol.tools, f"{name} has no tools"
    for t in sol.tools:
        assert set(t) >= {"name", "description", "input_schema"}
        assert t["input_schema"]["type"] == "object"
        assert re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", t["name"])
        assert callable(sol.handlers[t["name"]])
    assert sol.requires_approval <= set(sol.tool_names)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_prompt_has_required_sections(name):
    prompt = (SOLUTIONS_DIR / name / "prompt.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## (.+)$", prompt, re.M)
    for section in REQUIRED_SECTIONS:
        assert section in headings, f"{name}: missing section '{section}'"
    examples = prompt.split("## Examples", 1)[1]
    assert len(re.findall(r"^Example \d", examples, re.M)) >= 3, f"{name}: needs 3 examples"


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_prompt_tool_names_exist_and_every_tool_is_documented(name):
    sol = load_solution(name)
    names = set(sol.tool_names)
    referenced = set(BACKTICK_IDENT.findall(sol.system_prompt))
    unknown = referenced - names
    assert not unknown, f"{name}: prompt references tools not in tools.json: {sorted(unknown)}"
    undocumented = {n for n in names if f"`{n}`" not in sol.system_prompt}
    assert not undocumented, f"{name}: tools not mentioned in prompt: {sorted(undocumented)}"


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_readme_has_sections_and_usd_price(name):
    readme = (SOLUTIONS_DIR / name / "README.md").read_text(encoding="utf-8")
    for section in ("What it does", "Integrations", "KPIs", "Setup", "Guardrails", "Price (USD)"):
        assert f"## {section}" in readme, f"{name}: README missing {section}"
    assert re.search(r"\$\d[\d,]*", readme.split("## Price (USD)")[1])


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_fixtures_exist(name):
    fixtures = SOLUTIONS_DIR / name / "fixtures"
    assert fixtures.is_dir() and any(fixtures.rglob("*.*"))


def test_tools_json_files_are_valid_json():
    for path in SOLUTIONS_DIR.glob("*/tools.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data["tools"], list)
        assert isinstance(data.get("requires_approval", []), list)


def test_no_emojis_in_repo_text_files():
    offenders = []
    for path in ROOT.rglob("*"):
        if path.suffix in {".py", ".md", ".json", ".txt", ".csv", ".ini"} and "__pycache__" not in path.parts:
            if EMOJI.search(path.read_text(encoding="utf-8")):
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, offenders


def test_approval_gates_match_spec():
    gates = {name: load_solution(name).requires_approval for name in EXPECTED}
    assert "edit_order_address" in gates["support_wismo"]
    assert "map_sku" in gates["sync_exception"]
    assert "create_draft_order" in gates["po_to_order"]
    assert "draft_email" in gates["lead_triage"]
    assert "write_metafields" in gates["gpsr_extractor"]


def test_top_level_readme_lists_every_solution_with_price():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in EXPECTED:
        assert name in readme
    assert "$2,500-6,000 setup + $300-900/mo" in readme
