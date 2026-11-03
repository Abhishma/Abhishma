"""Guardrail helpers shared by the runner and solution handlers."""

from __future__ import annotations

import uuid
from typing import Any


def pending_approval(tool: str, tool_input: dict, reason: str = "requires human approval") -> dict:
    """The object returned to the model instead of executing a gated action.

    Handlers may also return this themselves (for example when only some
    arguments of a tool are safe to auto-apply).
    """
    return {
        "status": "pending_approval",
        "approval_id": f"appr_{uuid.uuid4().hex[:10]}",
        "tool": tool,
        "input": tool_input,
        "reason": reason,
        "message_for_model": (
            "This action was NOT executed. It has been queued for a human to "
            "approve. Tell the user it is pending review; do not claim it is done."
        ),
    }


def is_pending(result: Any) -> bool:
    return isinstance(result, dict) and result.get("status") == "pending_approval"


_JSON_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def validate_input(schema: dict, tool_input: Any) -> list[str]:
    """Light JSON-schema check (required keys, top-level types, enums).

    This is not a full validator; it catches the common model mistakes before
    a handler runs. Use strict tool definitions in production as well.
    """
    errors: list[str] = []
    if not isinstance(tool_input, dict):
        return ["tool input must be a JSON object"]
    for key in schema.get("required", []):
        if key not in tool_input:
            errors.append(f"missing required field '{key}'")
    props = schema.get("properties", {})
    for key, value in tool_input.items():
        spec = props.get(key)
        if spec is None:
            if schema.get("additionalProperties") is False:
                errors.append(f"unexpected field '{key}'")
            continue
        expected = spec.get("type")
        types = expected if isinstance(expected, list) else [expected] if expected else []
        if types and value is not None:
            py = tuple(t for name in types if name in _JSON_TYPES for t in
                       (_JSON_TYPES[name] if isinstance(_JSON_TYPES[name], tuple) else (_JSON_TYPES[name],)))
            # bool is a subclass of int; do not accept True for an integer field
            if py and (not isinstance(value, py) or (isinstance(value, bool) and "boolean" not in types)):
                errors.append(f"field '{key}' should be {expected}")
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"field '{key}' must be one of {spec['enum']}")
    return errors
