"""The agent runner: a small, explicit tool-use loop over the Messages API.

Loop:
  1. send system prompt + tools + conversation to the model
  2. if the model asks for tools, validate input, apply guardrails, dispatch to
     the Python handler, and return ALL tool results in one user message
  3. repeat until the model stops asking for tools, refuses, or max_turns hits

Guardrails:
  - max_turns caps model calls per run
  - tools listed in requires_approval are never executed by the runner; the
    model receives a pending-approval object and the request is queued in
    RunResult.pending_approvals for a human (see AgentRunner.approve)
  - handler exceptions become is_error tool results instead of crashing
  - transcripts are PII-redacted before they are written to disk
"""

from __future__ import annotations

import inspect
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from . import config
from .guardrails import is_pending, pending_approval, validate_input
from .loader import Solution, load_solution
from .redact import redact

Approver = Callable[[str, dict], bool]


def _block_to_dict(block: Any) -> dict:
    """Normalise SDK content blocks and plain dicts to plain dicts."""
    if isinstance(block, dict):
        return block
    if hasattr(block, "model_dump"):
        return block.model_dump(mode="json", exclude_none=True)
    raise TypeError(f"unsupported content block: {block!r}")


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _usage_dict(usage: Any) -> dict:
    if usage is None:
        return {}
    if isinstance(usage, dict):
        return usage
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json", exclude_none=True)
    return {}


def _to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


@dataclass
class RunResult:
    run_id: str
    final_text: str
    stop_reason: str  # end_turn | max_turns | refusal | max_tokens | error
    messages: list[dict]
    tool_calls: list[dict] = field(default_factory=list)
    pending_approvals: list[dict] = field(default_factory=list)
    transcript: dict = field(default_factory=dict)
    transcript_path: str | None = None


class AgentRunner:
    def __init__(
        self,
        solution: Solution | str,
        client: Any,
        model: str = config.DEFAULT_MODEL,
        max_turns: int = config.DEFAULT_MAX_TURNS,
        max_tokens: int = config.DEFAULT_MAX_TOKENS,
        transcript_dir: str | Path | None = None,
        approver: Approver | None = None,
        auto_approve: set[str] | None = None,
        use_server_fallbacks: bool = config.SERVER_FALLBACKS,
        effort: str | None = None,
        system_suffix: str = "",
    ):
        self.solution = load_solution(solution) if isinstance(solution, str) else solution
        self.client = client
        self.model = model
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.transcript_dir = Path(transcript_dir) if transcript_dir else (
            Path(config.TRANSCRIPT_DIR) if config.TRANSCRIPT_DIR else None
        )
        self.approver = approver
        self.auto_approve = set(auto_approve or ())
        # Haiku has no server-side fallback; only use it on Sonnet/Opus models.
        self.use_server_fallbacks = use_server_fallbacks and "haiku" not in model
        self.effort = effort
        self.system_suffix = system_suffix
        self._pending: dict[str, dict] = {}

    # ------------------------------------------------------------------ API

    def run(self, user_input: str | list[dict], context: dict | None = None) -> RunResult:
        """Run one conversation turn to completion.

        user_input: a user message string, or a full prior message list to
        continue a conversation. context: optional dict appended to the system
        prompt as JSON (business id, market, channel, current date ...).
        """
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        messages: list[dict] = (
            [{"role": "user", "content": user_input}] if isinstance(user_input, str)
            else [dict(m) for m in user_input]
        )
        system = self.solution.system_prompt
        if context:
            system += "\n\n## Runtime context\n```json\n" + _to_json(context) + "\n```\n"
        if self.system_suffix:
            system += "\n\n" + self.system_suffix

        events: list[dict] = []
        tool_calls: list[dict] = []
        pending: list[dict] = []
        final_text, stop = "", "end_turn"
        started = time.time()

        for turn in range(1, self.max_turns + 1):
            response = self._call_model(system, messages)
            content = [_block_to_dict(b) for b in (_get(response, "content") or [])]
            stop = _get(response, "stop_reason") or "end_turn"
            events.append({
                "type": "model_response", "turn": turn, "stop_reason": stop,
                "content": content, "usage": _usage_dict(_get(response, "usage")),
            })
            # Append the full content (including any thinking blocks) unchanged.
            messages.append({"role": "assistant", "content": content})
            final_text = "\n".join(b.get("text", "") for b in content if b.get("type") == "text").strip()

            if stop == "refusal":
                break
            tool_uses = [b for b in content if b.get("type") == "tool_use"]
            if stop != "tool_use" or not tool_uses:
                break

            results = []
            for block in tool_uses:
                record = self._dispatch(block)
                tool_calls.append(record)
                events.append({"type": "tool_call", "turn": turn, **record})
                if record["status"] == "pending_approval":
                    pending.append(record["result"])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": _to_json(record["result"]),
                    **({"is_error": True} if record["status"] == "error" else {}),
                })
            # All results for one assistant turn go back in a single user message.
            messages.append({"role": "user", "content": results})
        else:
            stop = "max_turns"
            events.append({"type": "guardrail", "detail": f"max_turns={self.max_turns} reached"})

        transcript = {
            "run_id": run_id,
            "solution": self.solution.name,
            "model": self.model,
            "started_at": started,
            "duration_s": round(time.time() - started, 3),
            "stop_reason": stop,
            "events": events,
            "pending_approvals": pending,
            "final_text": final_text,
        }
        redacted = redact(transcript)
        path = None
        if self.transcript_dir:
            self.transcript_dir.mkdir(parents=True, exist_ok=True)
            path = str(self.transcript_dir / f"{run_id}.json")
            Path(path).write_text(json.dumps(redacted, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

        return RunResult(
            run_id=run_id, final_text=final_text, stop_reason=stop, messages=messages,
            tool_calls=tool_calls, pending_approvals=pending, transcript=redacted,
            transcript_path=path,
        )

    def approve(self, approval_id: str) -> Any:
        """Execute a previously queued action after a human approved it."""
        item = self._pending.pop(approval_id, None)
        if item is None:
            raise KeyError(f"unknown or already processed approval {approval_id}")
        handler = self.solution.handlers[item["tool"]]
        # Handlers that gate some arguments themselves accept approved=True.
        if "approved" in inspect.signature(handler).parameters:
            return handler(**item["input"], approved=True)
        return handler(**item["input"])

    def reject(self, approval_id: str) -> None:
        self._pending.pop(approval_id, None)

    # ------------------------------------------------------------ internals

    def _call_model(self, system: str, messages: list[dict]) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": messages,
        }
        if self.solution.tools:
            kwargs["tools"] = self.solution.tools
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}
        if self.use_server_fallbacks:
            # Server-side refusal fallback (Claude API only): if the primary
            # model declines, the API retries on a suitable model for us.
            return self.client.beta.messages.create(
                betas=[config.SERVER_FALLBACK_BETA], fallbacks="default", **kwargs
            )
        return self.client.messages.create(**kwargs)

    def _dispatch(self, block: dict) -> dict:
        name, tool_input = block.get("name"), block.get("input") or {}
        base = {"tool_use_id": block.get("id"), "name": name, "input": tool_input}
        handler = self.solution.handlers.get(name)
        schema = next((t for t in self.solution.tools if t["name"] == name), None)
        if handler is None or schema is None:
            return {**base, "status": "error", "result": {"error": f"unknown tool '{name}'"}}

        errors = validate_input(schema.get("input_schema", {}), tool_input)
        if errors:
            return {**base, "status": "error", "result": {"error": "invalid input", "details": errors}}

        if name in self.solution.requires_approval and name not in self.auto_approve:
            approved = bool(self.approver and self.approver(name, tool_input))
            if not approved:
                result = pending_approval(name, tool_input)
                self._pending[result["approval_id"]] = result
                return {**base, "status": "pending_approval", "result": result}

        try:
            result = handler(**tool_input)
        except Exception as exc:  # handler bugs or upstream API failures
            return {**base, "status": "error", "result": {"error": type(exc).__name__, "message": str(exc)}}

        if is_pending(result):
            self._pending[result["approval_id"]] = result
            return {**base, "status": "pending_approval", "result": result}
        return {**base, "status": "ok", "result": result}
