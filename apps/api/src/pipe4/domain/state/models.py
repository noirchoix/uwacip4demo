from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from pipe4.domain.evidence.models import EvidenceRef

from .enums import (
    EpistemicStatus,
    PresentationKind,
    PublishedStateLifecycle,
    StateType,
    UserFacingStateStatus,
    VerificationStatus,
    VisibilityScope,
)
from .identity import StateIdentity
from .values import StateValue


class ConfidenceBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_reliability: float = Field(ge=0, le=1)
    evidence_quality: float = Field(ge=0, le=1)
    corroboration: float = Field(ge=0, le=1)
    recency: float = Field(ge=0, le=1)
    location_quality: float = Field(ge=0, le=1)
    weighted_score: float = Field(ge=0, le=1)
    policy_version: str


class StateVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_version_id: str = Field(default_factory=lambda: str(uuid4()))
    identity: StateIdentity
    value: StateValue

    epistemic_status: EpistemicStatus
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    lifecycle_status: PublishedStateLifecycle = PublishedStateLifecycle.CURRENT

    observed_at: datetime
    received_at: datetime
    valid_from: datetime
    expires_at: datetime | None = None
    last_verified_at: datetime | None = None

    confidence: float = Field(ge=0, le=1)
    confidence_breakdown: ConfidenceBreakdown | None = None
    policy_version: str

    visibility: VisibilityScope = VisibilityScope.PUBLIC
    permission_tags: set[str] = Field(default_factory=set)

    source_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

    predecessor_state_version_id: str | None = None
    version: int = Field(default=1, ge=1)
    correlation_id: str | None = None
    created_at: datetime

    @field_validator("observed_at", "received_at", "valid_from", "expires_at", "last_verified_at", "created_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("state timestamps must be timezone-aware")
        return value


class CurrentStateProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity_key: str
    state_version_id: str
    updated_at: datetime


class ProvenanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_count: int = 0
    evidence_count: int = 0
    independent_origin_count: int = 0
    public_source_labels: list[str] = Field(default_factory=list)


class EntitySummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    entity_id: str
    display_name: str | None = None
    entity_type: str | None = None
    distance_m: float | None = None


class CurrentStatePresentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: PresentationKind
    status: UserFacingStateStatus
    entity: EntitySummary
    identity: StateIdentity | None = None
    state_type: StateType | None = None
    value: StateValue | None = None
    observed_at: datetime | None = None
    expires_at: datetime | None = None
    freshness_seconds: int | None = None
    confidence: float | None = None
    epistemic_status: EpistemicStatus | None = None
    verification_status: VerificationStatus | None = None
    provenance: ProvenanceSummary | None = None
    state_version_id: str | None = None
    access_request_status: str | None = None
    actions: list[str] = Field(default_factory=list)
    message: str | None = None


class StateHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_version_id: str
    status: PublishedStateLifecycle
    state_type: StateType
    value: StateValue
    observed_at: datetime
    created_at: datetime
    epistemic_status: EpistemicStatus
    verification_status: VerificationStatus
    confidence: float
