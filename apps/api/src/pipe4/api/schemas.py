from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from pipe4.domain.access.models import AccessRequest
from pipe4.domain.acquisition.models import DecisionContext, StateRequest, TargetedAcquisitionRequest
from pipe4.domain.entities.models import EntityResolutionResult, ReferenceEntity
from pipe4.domain.observation.models import ObservationRecord
from pipe4.domain.state.enums import EpistemicStatus, StateType, VisibilityScope
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.models import CurrentStatePresentation, StateHistoryEntry, StateVersion
from pipe4.domain.state.values import StateValue
from pipe4.domain.watch.models import WatchCondition, WatchSubscription
from pipe4.application.nearby import NearbyResult
from pipe4.application.witness import WitnessInterpretationResult


class IdentityBody(BaseModel):
    model_config=ConfigDict(extra='forbid')
    entity_id: str
    object_key: str='main'
    state_type: StateType
    location_key: str | None=None
    qualifiers: dict[str,str|int|float|bool]=Field(default_factory=dict)
    def domain(self) -> StateIdentity: return StateIdentity.model_validate(self.model_dump())


class DeclarationRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    identity: IdentityBody
    value: StateValue
    observed_at: datetime
    source_id: str
    visibility: VisibilityScope=VisibilityScope.PUBLIC
    permission_tags: set[str]=Field(default_factory=set)
    idempotency_key: str | None=Field(default=None,max_length=200)


class ObservationRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    identity: IdentityBody
    value: StateValue
    observed_at: datetime
    source_id: str | None=None
    latitude: float | None=Field(default=None,ge=-90,le=90)
    longitude: float | None=Field(default=None,ge=-180,le=180)
    location_accuracy_m: float | None=Field(default=None,ge=0)
    location_description: str | None=Field(default=None,max_length=500)


class StateRequestBody(BaseModel):
    model_config=ConfigDict(extra='forbid')
    identity: IdentityBody
    decision_context: DecisionContext=Field(default_factory=DecisionContext)


class RevalidateRequest(StateRequestBody):
    state_version_id: str | None=None


class AccessCreateRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    entity_id: str
    identity_key: str | None=None
    permission: str='READ'
    scope: dict[str,str|int|float|bool]=Field(default_factory=dict)


class AccessDecisionRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    reason: str | None=Field(default=None,max_length=500)
    expires_at: datetime | None=None


class WatchCreateRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    condition: WatchCondition


class WitnessInterpretRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    text: str=Field(min_length=1,max_length=4000)
    latitude: float | None=Field(default=None,ge=-90,le=90)
    longitude: float | None=Field(default=None,ge=-180,le=180)


class WitnessReportRequest(WitnessInterpretRequest):
    observed_at: datetime
    entity_id: str | None=None
    object_key: str='main'
    state_type: StateType | None=None
    value: StateValue | None=None
    location_accuracy_m: float | None=Field(default=None,ge=0)
    location_description: str | None=Field(default=None,max_length=500)
    targeted_request_id: str | None=None


class WitnessReportReceipt(BaseModel):
    model_config=ConfigDict(extra='forbid')
    interpretation: WitnessInterpretationResult | None=None
    observation: ObservationRecord | None=None
    you_reported: str
    uwaci_status: str


class EntityResolveRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    text: str=Field(min_length=1,max_length=500)
    latitude: float | None=Field(default=None,ge=-90,le=90)
    longitude: float | None=Field(default=None,ge=-180,le=180)
    radius_m: int=Field(default=5000,gt=0,le=50000)


class ProvisionalEntityRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    entity_type: str=Field(min_length=1,max_length=120)
    display_name: str=Field(min_length=1,max_length=240)
    latitude: float | None=Field(default=None,ge=-90,le=90)
    longitude: float | None=Field(default=None,ge=-180,le=180)


class TargetedOfferRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    state_request_id: str
    target_subject: str
    ttl_seconds: int=Field(default=900,ge=60,le=86400)
    reward_label: str | None=Field(default=None,max_length=120)


class VerificationRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    observation_id: str


class SourceOutcomeRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    source_id: str
    entity_id: str
    state_type: StateType
    correct: bool


class SourceCreateRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    source_id: str
    source_type: str
    authority_scopes: set[str]=Field(default_factory=set)
    reliability: float=Field(default=0.5,ge=0,le=1)
    evidence_capability: float=Field(default=0.5,ge=0,le=1)
    expected_latency_ms: int=Field(default=1000,ge=0)
    cost_units: float=Field(default=0,ge=0)
    provider_key: str | None=None


class DisputeRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    identity: IdentityBody
    reason: str=Field(min_length=1,max_length=1000)
    proposed_value: StateValue | None=None
    observed_at: datetime | None=None
    latitude: float | None=Field(default=None,ge=-90,le=90)
    longitude: float | None=Field(default=None,ge=-180,le=180)
    location_accuracy_m: float | None=Field(default=None,ge=0)
    location_description: str | None=Field(default=None,max_length=500)
