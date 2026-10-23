"""Shared fixtures: fixed clock, no API key, fresh handler state per test."""

import importlib
import os

import pytest

os.environ["MARGINWISE_NOW"] = "2026-10-17T12:00:00+10:00"
os.environ.pop("ANTHROPIC_API_KEY", None)

from core.loader import list_solutions  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_handler_state(monkeypatch):
    monkeypatch.setenv("MARGINWISE_NOW", "2026-10-17T12:00:00+10:00")
    for name in list_solutions():
        mod = importlib.import_module(f"solutions.{name}.handlers")
        if hasattr(mod, "reset_state"):
            mod.reset_state()
    yield
