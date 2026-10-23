"""Small helpers for mock handlers backed by fixture files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_csv(path: Path | str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def not_found(kind: str, key: Any) -> dict:
    return {"found": False, "error": f"{kind} '{key}' not found"}


def now():
    """Current time, overridable with MARGINWISE_NOW (ISO 8601) for tests and demos."""
    import os
    from datetime import datetime, timezone

    fixed = os.getenv("MARGINWISE_NOW")
    if fixed:
        return datetime.fromisoformat(fixed)
    return datetime.now(timezone.utc)


def parse_dt(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value.replace("Z", "+00:00"))
