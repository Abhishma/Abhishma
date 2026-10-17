"""Marginwise core agent runner."""

from .clients import FakeClient, FakeResponse, fake_text, fake_tool_call, fake_tool_calls, make_client
from .guardrails import pending_approval, is_pending
from .loader import Solution, list_solutions, load_solution
from .redact import redact, redact_text
from .runner import AgentRunner, RunResult
from .llm import complete

__all__ = [
    "AgentRunner", "RunResult", "Solution", "load_solution", "list_solutions",
    "FakeClient", "FakeResponse", "fake_text", "fake_tool_call", "fake_tool_calls",
    "make_client", "pending_approval", "is_pending", "redact", "redact_text", "complete",
]
