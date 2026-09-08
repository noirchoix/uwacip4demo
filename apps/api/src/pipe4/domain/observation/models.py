from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from pipe4.domain.state.enums import EpistemicStatus
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import StateValue


class ObservationStatus(StrEnum):
    RECEIVED = "RECEIVED"
    INTERPRETED = "INTERPRETED"
    ENTITY_RESOLVED = "ENTITY_RESOLVED"
    ACCEPTED_AS_EVIDENCE = "ACCEPTED_AS_EVIDENCE"
    VERIFYING = "VERIFYING"
    CONSUMED = "CONSUMED"
    REJECTED = "REJECTED"


class LocationEvidenceType(StrEnum):
    GPS_CONFIRMED = "GPS_CONFIRMED"
    MANUALLY_DESCRIBED = "MANUALLY_DESCRIBED"
    UNKNOWN = "UNKNOWN"


class ObservationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    identity: StateIdentity
    proposed_value: StateValue
    source_id: str
    actor_subject: str | None = None
    epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED
    status: ObservationStatus = ObservationStatus.RECEIVED
    observed_at: datetime
    received_at: datetime

    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    location_accuracy_m: float | None = Field(default=None, ge=0)
    location_description: str | None = Field(default=None, max_length=500)
    location_evidence_type: LocationEvidenceType = LocationEvidenceType.UNKNOWN

    evidence_ids: list[str] = Field(default_factory=list)
    original_input_ref: str | None = None
    interpretation_confidence: float | None = Field(default=None, ge=0, le=1)
    consumed_state_version_id: str | None = None
    correlation_id: str | None = None

    @field_validator("observed_at", "received_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("observation timestamps must be timezone-aware")
        return value
