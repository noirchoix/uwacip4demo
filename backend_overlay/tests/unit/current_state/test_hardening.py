from dataclasses import is_dataclass
from datetime import UTC, datetime, timedelta
from inspect import signature
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import UniqueConstraint

from app.modules.current_state.domain.access import AccessRequest, AccessScope
from app.modules.current_state.domain.enums import (
    AccessPermission,
    AccessRequestStatus,
    EpistemicStatus,
    StateType,
    VerificationStatus,
    WatchOperator,
)
from app.modules.current_state.domain.idempotency import IdempotencyContext
from app.modules.current_state.domain.identity import StateIdentity
from app.modules.current_state.domain.nearby import (
    NearbyRankingPolicy,
    NearbySignals,
    rank_nearby,
)
from app.modules.current_state.domain.observation import ObservationRecord
from app.modules.current_state.domain.state import StateVersion
from app.modules.current_state.domain.values import BooleanStateValue
from app.modules.current_state.domain.watch import WatchCondition, WatchSubscription
from app.modules.current_state.models.models import CurrentStateObservationModel
from app.modules.current_state.ports.repository import CurrentStateRepository
from app.modules.current_state.schemas.contracts import AccessCreateRequest, WatchConditionRequest

ENTITY = UUID("11111111-1111-4111-8111-111111111111")
USER = UUID("22222222-2222-4222-8222-222222222222")
DECIDER = UUID("33333333-3333-4333-8333-333333333333")
NOW = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)


def test_watch_contract_rejects_unknown_operator_and_non_scalar_target() -> None:
    identity = StateIdentity(entity_id=ENTITY, state_type=StateType.AVAILABLE)

    with pytest.raises(ValidationError):
        WatchCondition(identity=identity, operator="contains_everything", target=True)

    with pytest.raises(ValidationError):
        WatchCondition(identity=identity, operator=WatchOperator.EQ, target={"value": True})


def test_watch_threshold_operators_require_numeric_target() -> None:
    identity = StateIdentity(entity_id=ENTITY, state_type=StateType.TIME)

    with pytest.raises(ValidationError):
        WatchCondition(identity=identity, operator=WatchOperator.LT, target="15 minutes")

    condition = WatchCondition(
        identity=identity,
        operator=WatchOperator.LT,
        target=900,
        field_path="seconds",
    )
    assert condition.target == 900


def test_api_watch_schema_uses_same_typed_condition_contract() -> None:
    identity = StateIdentity(entity_id=ENTITY, state_type=StateType.WORKING)
    request = WatchConditionRequest(
        identity=identity,
        operator=WatchOperator.EQ,
        target=True,
    )
    assert request.operator is WatchOperator.EQ


def test_access_scope_is_typed_and_canonicalized() -> None:
    scope = AccessScope(
        state_types=(StateType.WORKING, StateType.AVAILABLE, StateType.WORKING),
        object_keys=("x-ray", "atm", "x-ray"),
        field_paths=("value", "value"),
    )
    assert scope.state_types == (StateType.AVAILABLE, StateType.WORKING)
    assert scope.object_keys == ("atm", "x-ray")
    assert scope.field_paths == ("value",)



def test_access_scope_rejects_empty_or_ambiguous_full_scope() -> None:
    with pytest.raises(ValidationError):
        AccessScope()

    with pytest.raises(ValidationError):
        AccessScope(
            all_current_state=True,
            state_types=(StateType.WORKING,),
        )

def test_approved_access_request_requires_auditable_decision_and_approved_scope() -> None:
    scope = AccessScope(state_types=(StateType.WORKING,))

    with pytest.raises(ValueError):
        AccessRequest(
            requester_user_id=USER,
            target_entity_id=ENTITY,
            requested_permission=AccessPermission.READ,
            requested_scope=scope,
            status=AccessRequestStatus.APPROVED,
            requested_at=NOW,
        )

    request = AccessRequest(
        requester_user_id=USER,
        target_entity_id=ENTITY,
        requested_permission=AccessPermission.READ,
        requested_scope=scope,
        approved_scope=scope,
        status=AccessRequestStatus.APPROVED,
        requested_at=NOW,
        decision_actor_user_id=DECIDER,
        decided_at=NOW,
    )
    assert request.approved_scope == scope



def test_approved_scope_cannot_broaden_requested_access() -> None:
    requested = AccessScope(state_types=(StateType.WORKING,))
    broader = AccessScope(all_current_state=True)

    with pytest.raises(ValueError):
        AccessRequest(
            requester_user_id=USER,
            target_entity_id=ENTITY,
            requested_scope=requested,
            approved_scope=broader,
            status=AccessRequestStatus.APPROVED,
            requested_at=NOW,
            decision_actor_user_id=DECIDER,
            decided_at=NOW,
        )

    narrowed = AccessScope(
        state_types=(StateType.WORKING,),
        field_paths=("value",),
    )
    request = AccessRequest(
        requester_user_id=USER,
        target_entity_id=ENTITY,
        requested_scope=requested,
        approved_scope=narrowed,
        status=AccessRequestStatus.APPROVED,
        requested_at=NOW,
        decision_actor_user_id=DECIDER,
        decided_at=NOW,
    )
    assert request.approved_scope == narrowed

def test_access_create_schema_defaults_to_explicit_entity_read_scope() -> None:
    request = AccessCreateRequest(target_entity_id=ENTITY)
    assert request.requested_permission is AccessPermission.READ
    assert request.requested_scope.all_current_state is True



def test_access_create_defaults_to_identity_scope_when_identity_is_targeted() -> None:
    identity_key = "A" * 64
    request = AccessCreateRequest(
        target_entity_id=ENTITY,
        target_identity_key=identity_key,
    )
    assert request.target_identity_key == identity_key.lower()
    assert request.requested_scope.all_current_state is False
    assert request.requested_scope.identity_keys == (identity_key.lower(),)

def test_access_identity_key_rejects_non_hex_values() -> None:
    with pytest.raises(ValueError):
        AccessRequest(
            requester_user_id=USER,
            target_entity_id=ENTITY,
            requested_scope=AccessScope(all_current_state=True),
            target_identity_key="z" * 64,
            requested_at=NOW,
        )

    with pytest.raises(ValidationError):
        AccessCreateRequest(
            target_entity_id=ENTITY,
            target_identity_key="not-a-state-identity-key",
        )


def test_idempotency_context_uses_host_aligned_bounds_and_request_hash() -> None:
    request_hash = "a" * 64
    context = IdempotencyContext(
        user_id=USER,
        operation="witness_report",
        key="mobile-request-001",
        request_hash=request_hash,
    )
    assert context.request_hash == request_hash

    with pytest.raises(ValueError):
        IdempotencyContext(
            user_id=USER,
            operation="witness_report",
            key="k" * 129,
            request_hash=request_hash,
        )
    with pytest.raises(ValueError):
        IdempotencyContext(
            user_id=USER,
            operation="witness_report",
            key="key",
            request_hash="A" * 64,
        )
    with pytest.raises(ValueError):
        IdempotencyContext(
            user_id=USER,
            operation="   ",
            key="key",
            request_hash=request_hash,
        )
    with pytest.raises(ValueError):
        IdempotencyContext(
            user_id=USER,
            operation="witness_report",
            key="   ",
            request_hash=request_hash,
        )


def test_internal_domain_records_follow_host_dataclass_style() -> None:
    assert is_dataclass(StateVersion)
    assert is_dataclass(ObservationRecord)
    assert is_dataclass(AccessRequest)
    assert is_dataclass(WatchSubscription)


def test_state_version_dataclass_preserves_validation() -> None:
    identity = StateIdentity(entity_id=ENTITY, state_type=StateType.WORKING)
    with pytest.raises(ValueError):
        StateVersion(
            identity=identity,
            value=BooleanStateValue(value=True),
            epistemic_status=EpistemicStatus.OBSERVED,
            verification_status=VerificationStatus.VERIFIED,
            confidence=1.5,
            observed_at=NOW,
            valid_from=NOW,
            created_at=NOW,
        )


def test_nearby_ranking_policy_is_explicit_and_configurable() -> None:
    near_low_priority = NearbySignals(
        distance_m=50,
        observed_at=NOW - timedelta(minutes=5),
        verified=True,
        intent_match=0.1,
        urgency=0.0,
    )
    farther_urgent = NearbySignals(
        distance_m=400,
        observed_at=NOW - timedelta(minutes=5),
        verified=True,
        intent_match=1.0,
        urgency=1.0,
    )
    policy = NearbyRankingPolicy(
        proximity_weight=0.05,
        freshness_weight=0.05,
        verification_weight=0.05,
        intent_weight=0.35,
        urgency_weight=0.50,
    )

    assert rank_nearby(farther_urgent, now=NOW, policy=policy).relevance_score > rank_nearby(
        near_low_priority, now=NOW, policy=policy
    ).relevance_score


def test_nearby_policy_rejects_zero_total_weight() -> None:
    with pytest.raises(ValueError):
        NearbyRankingPolicy(
            proximity_weight=0,
            freshness_weight=0,
            verification_weight=0,
            intent_weight=0,
        )


def test_repository_contract_requires_atomic_publication_operation() -> None:
    methods = CurrentStateRepository.__dict__
    assert "publish_state_version" in methods
    assert "append_state_version" not in methods
    assert "replace_current_projection" not in methods
    params = signature(methods["publish_state_version"]).parameters
    assert "expected_current_state_version_id" in params



def test_observation_idempotency_requires_authenticated_actor_when_present() -> None:
    constraint = next(
        item
        for item in CurrentStateObservationModel.__table__.constraints
        if str(getattr(item, "name", "")).endswith(
            "ck_current_state_observation_idempotency_complete"
        )
    )
    assert "actor_user_id IS NOT NULL" in str(constraint.sqltext)

def test_observation_idempotency_constraint_is_scoped_like_host_backend() -> None:
    unique_constraints = {
        tuple(column.name for column in constraint.columns)
        for constraint in CurrentStateObservationModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("actor_user_id", "idempotency_operation", "idempotency_key") in unique_constraints
    assert CurrentStateObservationModel.__table__.c.idempotency_key.unique is not True
    assert "idempotency_request_hash" in CurrentStateObservationModel.__table__.c
