from __future__ import annotations

from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import (
    EpistemicStatus,
    PresentationKind,
    PublishedStateLifecycle,
    UserFacingStateStatus,
)
from pipe4.domain.state.models import (
    CurrentStatePresentation,
    EntitySummary,
    ProvenanceSummary,
    StateVersion,
)
from pipe4.ports.authorization import AuthorizationPort
from pipe4.ports.entities import EntityCatalogPort
from pipe4.ports.provenance import ProvenancePort
from pipe4.repositories.protocols import AccessRepository


class PresentationService:
    def __init__(self, *, authorization: AuthorizationPort, entities: EntityCatalogPort, provenance: ProvenancePort, access: AccessRepository) -> None:
        self.authorization=authorization; self.entities=entities; self.provenance=provenance; self.access=access

    async def unknown(self, *, entity_id: str, identity=None, message: str='Uwaci could not establish a current state.') -> CurrentStatePresentation:
        entity=await self.entities.get(entity_id)
        return CurrentStatePresentation(
            kind=PresentationKind.UNKNOWN,
            status=UserFacingStateStatus.UNKNOWN,
            entity=EntitySummary(entity_id=entity_id,display_name=entity.display_name if entity else None,entity_type=entity.entity_type if entity else None),
            identity=identity,
            state_type=identity.state_type if identity else None,
            actions=['request_refresh','watch'],
            message=message,
        )

    async def state(self, principal: Principal, state: StateVersion, *, freshness_seconds: int | None=None, status_override: UserFacingStateStatus | None=None, distance_m: float | None=None) -> CurrentStatePresentation:
        entity=await self.entities.get(state.identity.entity_id)
        summary=EntitySummary(entity_id=state.identity.entity_id,display_name=entity.display_name if entity else None,entity_type=entity.entity_type if entity else None,distance_m=distance_m)
        allowed=await self.authorization.can_view(principal,identity=state.identity,visibility=state.visibility,permission_tags=state.permission_tags)
        if not allowed:
            pending=await self.access.pending_request_status(subject=principal.subject,entity_id=state.identity.entity_id,identity_key=state.identity.key)
            return CurrentStatePresentation(
                kind=PresentationKind.PROTECTED,
                status=UserFacingStateStatus.UNKNOWN,
                entity=summary,
                access_request_status=pending,
                actions=['request_access'] if not pending else [],
                message='This current-state value is protected.',
            )
        status=status_override or self._status(state)
        labels=await self.provenance.public_source_labels(source_ids=state.source_ids,context_key=state.identity.key)
        provenance=ProvenanceSummary(source_count=len(set(state.source_ids)),evidence_count=len(set(state.evidence_ids)),independent_origin_count=len(set(labels)),public_source_labels=labels)
        return CurrentStatePresentation(
            kind=PresentationKind.STATE,
            status=status,
            entity=summary,
            identity=state.identity,
            state_type=state.identity.state_type,
            value=state.value,
            observed_at=state.observed_at,
            expires_at=state.expires_at,
            freshness_seconds=freshness_seconds,
            confidence=state.confidence,
            epistemic_status=state.epistemic_status,
            verification_status=state.verification_status,
            provenance=provenance,
            state_version_id=state.state_version_id,
            actions=['watch','report','revalidate'],
        )

    @staticmethod
    def _status(state: StateVersion) -> UserFacingStateStatus:
        if state.lifecycle_status == PublishedStateLifecycle.DISPUTED: return UserFacingStateStatus.DISPUTED
        if state.lifecycle_status == PublishedStateLifecycle.STALE: return UserFacingStateStatus.STALE
        if state.epistemic_status == EpistemicStatus.INFERRED: return UserFacingStateStatus.INFERRED
        return UserFacingStateStatus.CURRENT
