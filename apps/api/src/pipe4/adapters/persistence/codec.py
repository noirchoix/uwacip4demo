from __future__ import annotations

from pipe4.domain.access.models import AccessRequest, PermissionGrant
from pipe4.domain.acquisition.models import (
    AcquisitionAttempt,
    AcquisitionJob,
    StateRequest,
    TargetedAcquisitionRequest,
)
from pipe4.domain.contradiction import ContradictionRecord
from pipe4.domain.entities.models import ReferenceEntity
from pipe4.domain.events.models import DomainEvent, OutboxRecord
from pipe4.domain.observation.models import ObservationRecord
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.models import StateVersion
from pipe4.domain.watch.models import WatchProcess, WatchSubscription

from . import models as db


def state_to_row(state: StateVersion) -> db.StateVersionRow:
    data = state.model_dump(mode="json")
    identity = data.pop("identity")
    return db.StateVersionRow(
        state_version_id=state.state_version_id,
        identity_key=state.identity.key,
        entity_id=state.identity.entity_id,
        object_key=state.identity.object_key,
        state_type=state.identity.state_type.value,
        location_key=state.identity.location_key,
        qualifiers=state.identity.qualifiers,
        value=data["value"],
        epistemic_status=state.epistemic_status.value,
        verification_status=state.verification_status.value,
        lifecycle_status=state.lifecycle_status.value,
        observed_at=state.observed_at,
        received_at=state.received_at,
        valid_from=state.valid_from,
        expires_at=state.expires_at,
        last_verified_at=state.last_verified_at,
        confidence=state.confidence,
        confidence_breakdown=data["confidence_breakdown"],
        policy_version=state.policy_version,
        visibility=state.visibility.value,
        permission_tags=list(state.permission_tags),
        source_ids=state.source_ids,
        evidence_ids=state.evidence_ids,
        predecessor_state_version_id=state.predecessor_state_version_id,
        version=state.version,
        correlation_id=state.correlation_id,
        created_at=state.created_at,
    )


def row_to_state(row: db.StateVersionRow) -> StateVersion:
    return StateVersion.model_validate({
        "state_version_id": row.state_version_id,
        "identity": {
            "entity_id": row.entity_id,
            "object_key": row.object_key,
            "state_type": row.state_type,
            "location_key": row.location_key,
            "qualifiers": row.qualifiers or {},
        },
        "value": row.value,
        "epistemic_status": row.epistemic_status,
        "verification_status": row.verification_status,
        "lifecycle_status": row.lifecycle_status,
        "observed_at": row.observed_at,
        "received_at": row.received_at,
        "valid_from": row.valid_from,
        "expires_at": row.expires_at,
        "last_verified_at": row.last_verified_at,
        "confidence": row.confidence,
        "confidence_breakdown": row.confidence_breakdown,
        "policy_version": row.policy_version,
        "visibility": row.visibility,
        "permission_tags": set(row.permission_tags or []),
        "source_ids": row.source_ids or [],
        "evidence_ids": row.evidence_ids or [],
        "predecessor_state_version_id": row.predecessor_state_version_id,
        "version": row.version,
        "correlation_id": row.correlation_id,
        "created_at": row.created_at,
    })
