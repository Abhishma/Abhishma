"""Assistant adapters for the AEO visibility harness.

Each adapter exposes .name and .ask(question, market) -> answer text.

  FixtureAdapter     offline replay from fixtures/answers.json (tests, demos)
  AnthropicAdapter   real call through the Anthropic Messages API
  OpenAIAdapter      TODO stub
  PerplexityAdapter  TODO stub

Note: API answers differ from what consumers see in the chat apps (no
personalisation, different system prompts, sometimes no web search). Treat
API-based measurement as a consistent proxy and spot-check in the apps.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core import config
from core.fixtures import load_json

FIXTURES = Path(__file__).parent / "fixtures"


class FixtureAdapter:
    def __init__(self, name: str, answers: dict[str, str] | None = None):
        self.name = name
        self._answers = answers if answers is not None else load_json(FIXTURES / "answers.json").get(name, {})

    def ask(self, question: str, market: dict | None = None, question_id: str = "") -> str:
        return self._answers.get(question_id, "")


class AnthropicAdapter:
    """Asks Claude the buying question as a consumer would, with no brand hints."""

    name = "anthropic"

    def __init__(self, client: Any, model: str = config.DEFAULT_MODEL, use_web_search: bool = True):
        self.client = client
        self.model = model
        self.use_web_search = use_web_search

    def ask(self, question: str, market: dict | None = None, question_id: str = "") -> str:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": question}],
        }
        if self.use_web_search:
            # Server-side web search so answers reflect what a consumer with search would see.
            tool: dict = {"type": "web_search_20260209", "name": "web_search", "max_uses": 3}
            if market and market.get("country_code"):
                tool["user_location"] = {"type": "approximate", "country": market["country_code"],
                                         **({"city": market["city"]} if market.get("city") else {})}
            kwargs["tools"] = [tool]
        resp = self.client.messages.create(**kwargs)
        blocks = resp.content if not isinstance(resp, dict) else resp["content"]
        return "\n".join(
            (b.get("text", "") if isinstance(b, dict) else getattr(b, "text", "") or "")
            for b in blocks
            if (b.get("type") if isinstance(b, dict) else getattr(b, "type", "")) == "text"
        ).strip()


class OpenAIAdapter:
    """TODO(adapter): implement with the OpenAI Responses API (web search tool enabled),
    reading OPENAI_API_KEY. Kept as a stub: this package only ships the Anthropic SDK."""

    name = "openai"

    def ask(self, question: str, market: dict | None = None, question_id: str = "") -> str:
        raise NotImplementedError("OpenAI adapter not implemented; see TODO in adapters.py")


class PerplexityAdapter:
    """TODO(adapter): implement with the Perplexity Sonar chat completions API,
    reading PERPLEXITY_API_KEY; keep the returned citations for source analysis."""

    name = "perplexity"

    def ask(self, question: str, market: dict | None = None, question_id: str = "") -> str:
        raise NotImplementedError("Perplexity adapter not implemented; see TODO in adapters.py")
