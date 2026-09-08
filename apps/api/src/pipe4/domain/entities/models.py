from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class EntityResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


class ReferenceEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_id: str = Field(default_factory=lambda: str(uuid4()))
    entity_type: str
    display_name: str
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    aliases: list[str] = Field(default_factory=list)
    provisional: bool = False
    created_at: datetime


class EntityCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    entity_id: str
    display_name: str
    entity_type: str
    distance_m: float | None = None
    confidence: float = Field(ge=0, le=1)


class EntityResolutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EntityResolutionStatus
    candidates: list[EntityCandidate] = Field(default_factory=list)
    selected_entity_id: str | None = None
