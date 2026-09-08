from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from pipe4.domain.acquisition.models import DecisionContext
from pipe4.domain.observation.models import LocationEvidenceType
from pipe4.domain.state.enums import EpistemicStatus
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import StateValue


class AcquiredObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    value: StateValue
    observed_at_iso: str
    epistemic_status: EpistemicStatus
    evidence_payload: bytes | None = None
    evidence_content_type: str | None = None
    origin_key: str
    location_type: LocationEvidenceType = LocationEvidenceType.UNKNOWN
    latitude: float | None = None
    longitude: float | None = None
    location_accuracy_m: float | None = None


class AcquisitionSourcePort(Protocol):
    async def acquire(
        self,
        *,
        identity: StateIdentity,
        decision_context: DecisionContext,
    ) -> AcquiredObservation: ...
