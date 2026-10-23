"""Model clients: the real Anthropic SDK client and an offline FakeClient.

The runner only relies on a tiny surface:

    client.messages.create(**kwargs)        -> response
    client.beta.messages.create(**kwargs)   -> response   (server-side fallbacks)

where response has .content (list of blocks), .stop_reason and optionally
.usage. Blocks may be SDK objects or plain dicts; the runner normalises both.
"""

from __future__ import annotations

import copy
import os
import uuid
from dataclasses import dataclass, field
from typing import Any


def make_client() -> Any:
    """Return a real Anthropic client when ANTHROPIC_API_KEY is set.

    Raises RuntimeError otherwise so that nothing silently runs without a key.
    Tests should use FakeClient instead.
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export it for real runs, or pass a "
            "core.clients.FakeClient for offline tests and demos."
        )
    import anthropic  # imported lazily so tests never need network or a key

    return anthropic.Anthropic()


# ---------------------------------------------------------------------------
# Fake client for tests
# ---------------------------------------------------------------------------


def text_block(text: str) -> dict:
    return {"type": "text", "text": text}


def tool_use_block(name: str, tool_input: dict, block_id: str | None = None) -> dict:
    return {
        "type": "tool_use",
        "id": block_id or f"toolu_{uuid.uuid4().hex[:12]}",
        "name": name,
        "input": tool_input,
    }


@dataclass
class FakeResponse:
    content: list[dict]
    stop_reason: str = "end_turn"
    usage: dict = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})
    model: str = "fake"
    id: str = field(default_factory=lambda: f"msg_fake_{uuid.uuid4().hex[:8]}")


def fake_text(text: str) -> FakeResponse:
    """A scripted final answer."""
    return FakeResponse(content=[text_block(text)], stop_reason="end_turn")


def fake_tool_call(name: str, tool_input: dict, preamble: str | None = None) -> FakeResponse:
    """A scripted response that calls one tool."""
    blocks: list[dict] = []
    if preamble:
        blocks.append(text_block(preamble))
    blocks.append(tool_use_block(name, tool_input))
    return FakeResponse(content=blocks, stop_reason="tool_use")


def fake_tool_calls(calls: list[tuple[str, dict]]) -> FakeResponse:
    """A scripted response with several parallel tool calls."""
    return FakeResponse(content=[tool_use_block(n, i) for n, i in calls], stop_reason="tool_use")


class _FakeMessages:
    def __init__(self, parent: "FakeClient", channel: str):
        self._parent = parent
        self._channel = channel

    def create(self, **kwargs: Any) -> FakeResponse:
        return self._parent._next(self._channel, kwargs)


class _FakeBeta:
    def __init__(self, parent: "FakeClient"):
        self.messages = _FakeMessages(parent, "beta")


class FakeClient:
    """Replays scripted model responses in order and records every request.

    Example:
        client = FakeClient([
            fake_tool_call("get_order", {"order_id": "1001"}),
            fake_text("Your order shipped yesterday."),
        ])
    """

    def __init__(self, responses: list[FakeResponse | dict], repeat_last: bool = False):
        self._responses = list(responses)
        self._repeat_last = repeat_last
        self.calls: list[dict] = []
        self.messages = _FakeMessages(self, "standard")
        self.beta = _FakeBeta(self)

    def _next(self, channel: str, kwargs: dict) -> FakeResponse:
        # Deep copy so later mutation of the conversation does not alter the record.
        self.calls.append({"channel": channel, **copy.deepcopy(kwargs)})
        if not self._responses:
            raise AssertionError("FakeClient ran out of scripted responses")
        if len(self._responses) == 1 and self._repeat_last:
            item = self._responses[0]
        else:
            item = self._responses.pop(0)
        if isinstance(item, dict):
            item = FakeResponse(**item)
        # Fresh block ids each time when repeating, to mimic the real API.
        return copy.deepcopy(item)
