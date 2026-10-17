"""Single-call helpers (no tool loop): summaries, classification, extraction."""

from __future__ import annotations

from typing import Any

from . import config


def complete(
    client: Any,
    system: str,
    user: str,
    model: str = config.DEFAULT_MODEL,
    max_tokens: int = 4000,
) -> str:
    """One Messages API call; returns the concatenated text blocks."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    stop = response.get("stop_reason") if isinstance(response, dict) else getattr(response, "stop_reason", None)
    if stop == "refusal":
        raise RuntimeError("model declined the request (stop_reason=refusal)")
    blocks = response.get("content") if isinstance(response, dict) else response.content
    parts = []
    for b in blocks:
        btype = b.get("type") if isinstance(b, dict) else getattr(b, "type", None)
        if btype == "text":
            parts.append(b.get("text") if isinstance(b, dict) else b.text)
    return "\n".join(parts).strip()


def classify(client: Any, text: str, labels: list[str], instructions: str = "",
             model: str = config.CLASSIFY_MODEL) -> str:
    """Cheap single-label classification. Falls back to 'unknown' on bad output."""
    system = (
        "You are a classifier. Reply with exactly one label from this list and "
        f"nothing else: {', '.join(labels)}. {instructions}".strip()
    )
    answer = complete(client, system, text, model=model, max_tokens=50).strip().lower()
    for label in labels:
        if answer == label.lower():
            return label
    return "unknown"
