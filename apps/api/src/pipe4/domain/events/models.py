from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    aggregate_type: str
    aggregate_id: str
    occurred_at: datetime
    correlation_id: str | None = None
    payload: dict[str, str | int | float | bool | None | list[str]] = Field(default_factory=dict)


class OutboxRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outbox_id: str = Field(default_factory=lambda: str(uuid4()))
    event: DomainEvent
    created_at: datetime
    published_at: datetime | None = None
    attempts: int = Field(default=0, ge=0)
    last_error: str | None = None
