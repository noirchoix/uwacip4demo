from __future__ import annotations

import hashlib
import json

from pipe4.domain.state.values import StateValue
from pipe4.domain.watch.models import WatchCondition


def watch_fingerprint(condition: WatchCondition) -> str:
    payload = condition.model_dump(mode="json")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def evaluate_watch(operator: str, current: StateValue, target: StateValue) -> bool:
    if current.kind != target.kind:
        return False

    c = current.model_dump(mode="json")
    t = target.model_dump(mode="json")

    if operator == "EQ":
        return c == t
    if operator == "NEQ":
        return c != t

    def scalar(value: dict[str, object]) -> float | None:
        for key in ("value", "available", "seconds", "minimum"):
            raw = value.get(key)
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                return float(raw)
        return None

    left, right = scalar(c), scalar(t)
    if left is None or right is None:
        return False
    return {
        "GT": left > right,
        "GTE": left >= right,
        "LT": left < right,
        "LTE": left <= right,
    }.get(operator, False)
