from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.current_state.domain.access import AccessScope
from app.modules.current_state.domain.enums import (
    AccessPermission,
    AccessRequestStatus,
    EntityResolutionStatus,
    EpistemicStatus,
    LocationVerificationStatus,
    ObservationStatus,
    StateLifecycle,
    StateType,
    TargetedAcquisitionStatus,
    UserStateStatus,
    VerificationStatus,
    VisibilityScope,
    WatchOperator,
    WatchStatus,
)
from app.modules.current_state.domain.identity import ScalarQualifier, StateIdentity
from app.modules.current_state.domain.watch import WatchTarget
from app.modules.current_state.domain.values import StateValue


class Pipe4Entity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: UUID
    entity_type: str
    display_name: str
    latitude: float | None = None
    longitude: float | None = None
    administrative_area: str | None = None
    active: bool = True
    resolution_status: EntityResolutionStatus
    created_by_subject: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class Pipe4StateVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    state_version_id: UUID
    identity: StateIdentity
    value: StateValue
    lifecycle_status: StateLifecycle
    epistemic_status: EpistemicStatus
    verification_status: VerificationStatus
    confidence: float | None = Field(default=None, ge=0, le=1)
    observed_at: datetime
    expires_at: datetime | None = None
    visibility: VisibilityScope


class PublicSourcePresentation(BaseModel):
    role: str
    label: str


class CurrentStatePresentation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["STATE", "PROTECTED", "UNKNOWN"]
    entity: Pipe4Entity | None = None
    identity: StateIdentity | None = None
    state_version_id: UUID | None = None
    state_type: StateType | None = None
    value: StateValue | None = None
    status: UserStateStatus
    observed_at: datetime | None = None
    expires_at: datetime | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    verification_status: VerificationStatus | None = None
    provenance: list[PublicSourcePresentation] = Field(default_factory=list)
    access_request_status: AccessRequestStatus | None = None
    can_request_access: bool
    can_watch: bool
    can_report: bool
    explanation: str | None = None


class NearbyStateResult(BaseModel):
    state: Pipe4StateVersion
    entity: Pipe4Entity
    distance_m: float | None = Field(default=None, ge=0)
    relevance_score: float = Field(ge=0, le=1)
    ranking_breakdown: dict[str, float] = Field(default_factory=dict)


class WatchConditionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identity: StateIdentity
    operator: WatchOperator
    target: WatchTarget
    field_path: str | None = Field(default=None, max_length=120)
    decision_context: str | None = Field(default=None, max_length=80)
    permission_tags: list[str] = Field(default_factory=list)


class WatchSubscriptionResponse(BaseModel):
    subscription_id: UUID
    condition: WatchConditionRequest
    canonical_key: str
    subscriber: dict[str, object]
    status: WatchStatus
    active: bool
    created_at: datetime
    updated_at: datetime
    last_triggered_state_version_id: UUID | None = None
    last_condition_met: bool


class AccessRequestResponse(BaseModel):
    access_request_id: UUID
    requester_subject: str
    target_entity_id: UUID
    target_identity_key: str | None = None
    requested_permission: AccessPermission
    requested_scope: AccessScope
    approved_scope: AccessScope | None = None
    status: AccessRequestStatus
    requested_at: datetime
    decided_at: datetime | None = None
    decision_reason: str | None = None
    expires_at: datetime | None = None


class WitnessInterpretation(BaseModel):
    original_text: str
    inferred_state_type: StateType | None = None
    inferred_value: StateValue | None = None
    inferred_object_key: str | None = None
    confidence: float = Field(ge=0, le=1)
    clarification_question: str | None = None


class ObservationResponse(BaseModel):
    observation_id: UUID
    identity: StateIdentity
    value: StateValue
    status: ObservationStatus
    observed_at: datetime
    received_at: datetime
    location_verification_status: LocationVerificationStatus
    location_description: str | None = None


class WitnessReportReceipt(BaseModel):
    interpretation: WitnessInterpretation
    observation: ObservationResponse | None = None
    you_reported: object | None = None
    uwaci_status: Literal["VERIFYING", "CLARIFICATION_REQUIRED"]


class WitnessInterpretRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    object_hint: str | None = Field(default=None, max_length=240)


class WitnessReportRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    entity_id: UUID | None = None
    object_key: str = Field(default="reported_reality", min_length=1, max_length=200)
    observed_at: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    location_accuracy_m: float | None = Field(default=None, ge=0)
    location_description: str | None = Field(default=None, max_length=500)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)
    correlation_id: str | None = Field(default=None, max_length=120)
    targeted_request_id: UUID | None = None


class EntityResolveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_m: int = Field(default=5000, gt=0, le=50000)


class EntityCandidate(BaseModel):
    entity: Pipe4Entity
    distance_m: float | None = Field(default=None, ge=0)
    match_score: float = Field(ge=0, le=1)
    cue: str | None = None


class EntityResolutionResult(BaseModel):
    status: Literal["RESOLVED", "MULTIPLE_CANDIDATES", "NO_MATCH"]
    candidates: list[EntityCandidate] = Field(default_factory=list)
    entity: Pipe4Entity | None = None


class ProvisionalEntityRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class AccessCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_entity_id: UUID
    target_identity_key: str | None = Field(
        default=None, pattern=r"^[0-9a-fA-F]{64}$"
    )
    requested_scope: AccessScope = Field(
        default_factory=lambda: AccessScope(all_current_state=True)
    )
    requested_permission: AccessPermission = AccessPermission.READ

    @model_validator(mode="before")
    @classmethod
    def default_to_least_privilege_scope(cls, data: object) -> object:
        if not isinstance(data, dict) or "requested_scope" in data:
            return data
        values = dict(data)
        identity_key = values.get("target_identity_key")
        if isinstance(identity_key, str):
            values["requested_scope"] = {"identity_keys": [identity_key]}
        return values

    @field_validator("target_identity_key")
    @classmethod
    def canonicalize_target_identity_key(cls, value: str | None) -> str | None:
        return value.lower() if value is not None else None


class TargetedAcquisitionResponse(BaseModel):
    acquisition_request_id: UUID
    identity: StateIdentity
    target_subject: str
    status: TargetedAcquisitionStatus
    what_to_confirm: str
    approximate_distance_m: float | None = Field(default=None, ge=0)
    reward_amount: float | None = Field(default=None, ge=0)
    reward_currency: str | None = None
    offered_at: datetime
    witness_session_id: UUID | None = None


class WatchDeleteResponse(BaseModel):
    removed: bool = True
    subscription_id: UUID
