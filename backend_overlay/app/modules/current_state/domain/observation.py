from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.modules.current_state.domain.enums import (
    LocationVerificationStatus,
    ObservationStatus,
)
from app.modules.current_state.domain.identity import StateIdentity
from app.modules.current_state.domain.values import StateValue


@dataclass(frozen=True, slots=True)
class ObservationRecord:
    """Internal immutable observation record. Observation is evidence, not canonical truth."""

    identity: StateIdentity
    value: StateValue
    observed_at: datetime
    received_at: datetime
    observation_id: UUID = field(default_factory=uuid4)
    status: ObservationStatus = ObservationStatus.RECEIVED
    location_verification_status: LocationVerificationStatus = LocationVerificationStatus.UNKNOWN
    location_description: str | None = None
    actor_user_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None or self.received_at.tzinfo is None:
            raise ValueError("observation timestamps must be timezone-aware")
        if len(self.location_description or "") > 500:
            raise ValueError("location_description cannot exceed 500 characters")
