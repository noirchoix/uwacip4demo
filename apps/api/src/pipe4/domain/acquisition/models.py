from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from pipe4.domain.state.identity import StateIdentity


class StateRequestStatus(StrEnum):
    REQUESTED = "REQUESTED"
    ACQUIRING = "ACQUIRING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class GapReason(StrEnum):
    MISSING = "MISSING"
    STALE = "STALE"
    DISPUTED = "DISPUTED"
    INSUFFICIENT_CONFIDENCE = "INSUFFICIENT_CONFIDENCE"
    EXPLICIT_REVALIDATION = "EXPLICIT_REVALIDATION"
    UNKNOWN = "UNKNOWN"


class AcquisitionJobStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFYING = "VERIFYING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class AcquisitionAttemptStatus(StrEnum):
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    INADMISSIBLE = "INADMISSIBLE"


class TargetedAcquisitionStatus(StrEnum):
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"


class DecisionContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = "consumer_discovery"
    urgency: float = Field(default=0.5, ge=0, le=1)
    uncertainty_consequence: float = Field(default=0.25, ge=0, le=1)
    requested_quantity: float | None = Field(default=None, ge=0)
    unit: str | None = None


class StateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    identity: StateIdentity
    requester_subject: str
    decision_context: DecisionContext
    gap_reason: GapReason
    fingerprint: str
    status: StateRequestStatus = StateRequestStatus.REQUESTED
    demand_count: int = Field(default=1, ge=1)
    created_at: datetime
    updated_at: datetime
    resolved_state_version_id: str | None = None


class AcquisitionJob(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(default_factory=lambda: str(uuid4()))
    request_id: str
    identity: StateIdentity
    decision_context: DecisionContext
    status: AcquisitionJobStatus = AcquisitionJobStatus.PENDING
    candidate_source_ids: list[str] = Field(default_factory=list)
    idempotency_key: str
    created_at: datetime
    deadline_at: datetime
    updated_at: datetime


class AcquisitionAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt_id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    source_id: str
    status: AcquisitionAttemptStatus = AcquisitionAttemptStatus.STARTED
    started_at: datetime
    completed_at: datetime | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    cost_units: float = Field(default=0.0, ge=0)
    result_observation_id: str | None = None
    reason: str | None = None


class TargetedAcquisitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targeted_request_id: str = Field(default_factory=lambda: str(uuid4()))
    state_request_id: str
    target_subject: str
    status: TargetedAcquisitionStatus = TargetedAcquisitionStatus.OFFERED
    offered_at: datetime
    expires_at: datetime
    accepted_at: datetime | None = None
    completed_observation_id: str | None = None
    reward_label: str | None = None
