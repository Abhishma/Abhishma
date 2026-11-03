"""Command line entry point.

    python -m core.cli list
    python -m core.cli show receptionist
    python -m core.cli run receptionist "Hi, my aircon stopped working" \
        --context '{"business_id": "coolbreeze_ac"}' --transcripts ./transcripts

`run` needs ANTHROPIC_API_KEY. Gated tools are never executed from the CLI
unless --approve is passed (an interactive y/n prompt per action).
"""

from __future__ import annotations

import argparse
import json
import sys

from . import config
from .clients import make_client
from .loader import list_solutions, load_solution
from .runner import AgentRunner


def _ask(tool: str, tool_input: dict) -> bool:
    print(f"\nApproval needed for {tool}:\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}")
    return input("Approve? [y/N] ").strip().lower() == "y"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="marginwise")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("solution")
    run = sub.add_parser("run")
    run.add_argument("solution")
    run.add_argument("message")
    run.add_argument("--context", default="{}")
    run.add_argument("--model", default=config.DEFAULT_MODEL)
    run.add_argument("--max-turns", type=int, default=config.DEFAULT_MAX_TURNS)
    run.add_argument("--transcripts", default=None)
    run.add_argument("--approve", action="store_true", help="prompt to approve gated tools")
    args = parser.parse_args(argv)

    if args.cmd == "list":
        print("\n".join(list_solutions()))
        return 0
    if args.cmd == "show":
        sol = load_solution(args.solution)
        print(f"{sol.name}: {len(sol.tools)} tools; approval required for {sorted(sol.requires_approval)}")
        print("\n".join(f"  - {n}" for n in sol.tool_names))
        return 0

    runner = AgentRunner(
        args.solution, client=make_client(), model=args.model, max_turns=args.max_turns,
        transcript_dir=args.transcripts, approver=_ask if args.approve else None,
    )
    result = runner.run(args.message, context=json.loads(args.context))
    print(result.final_text)
    if result.pending_approvals:
        print(f"\n[{len(result.pending_approvals)} action(s) pending human approval]")
    print(f"\n[stop_reason={result.stop_reason} transcript={result.transcript_path}]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
