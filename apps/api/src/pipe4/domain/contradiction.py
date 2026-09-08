from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ContradictionStatus(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ContradictionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contradiction_id: str = Field(default_factory=lambda: str(uuid4()))
    identity_key: str
    incumbent_state_version_id: str
    competing_observation_id: str | None = None
    competing_state_version_id: str | None = None
    material: bool = True
    status: ContradictionStatus = ContradictionStatus.OPEN
    reason: str
    created_at: datetime
    resolved_at: datetime | None = None
