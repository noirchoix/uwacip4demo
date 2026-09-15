from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.modules.current_state.domain.enums import (
    EpistemicStatus,
    StateLifecycle,
    VerificationStatus,
    VisibilityScope,
)
from app.modules.current_state.domain.identity import StateIdentity
from app.modules.current_state.domain.values import StateValue


@dataclass(frozen=True, slots=True)
class StateVersion:
    """Internal immutable state-version record. New reality appends; it never overwrites history."""

    identity: StateIdentity
    value: StateValue
    epistemic_status: EpistemicStatus
    observed_at: datetime
    valid_from: datetime
    created_at: datetime
    state_version_id: UUID = field(default_factory=uuid4)
    lifecycle_status: StateLifecycle = StateLifecycle.CURRENT
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    confidence: float | None = None
    expires_at: datetime | None = None
    visibility: VisibilityScope = VisibilityScope.PUBLIC
    observation_ids: tuple[UUID, ...] = ()
    predecessor_state_version_id: UUID | None = None
    version: int = 1
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        for value in (self.observed_at, self.valid_from, self.created_at, self.expires_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("state timestamps must be timezone-aware")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1 when supplied")
        if self.version < 1:
            raise ValueError("state version must be at least 1")
        if len(self.correlation_id or "") > 120:
            raise ValueError("correlation_id cannot exceed 120 characters")
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValueError("observation_ids cannot contain duplicates")
