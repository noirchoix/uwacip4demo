from __future__ import annotations

import hashlib
import json
from datetime import datetime

from pipe4.domain.events.models import DomainEvent


def event(
    event_type: str,
    *,
    aggregate_type: str,
    aggregate_id: str,
    occurred_at: datetime,
    correlation_id: str | None = None,
    payload: dict[str, str | int | float | bool | None | list[str]] | None = None,
) -> DomainEvent:
    return DomainEvent(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        occurred_at=occurred_at,
        correlation_id=correlation_id,
        payload=payload or {},
    )


def fingerprint(payload: object) -> str:
    canonical=json.dumps(payload,sort_keys=True,separators=(',',':'),default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()
