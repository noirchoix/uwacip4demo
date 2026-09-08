from __future__ import annotations

import hashlib
from uuid import uuid4

from pipe4.domain.evidence.models import EvidenceClass, EvidenceRef, SourceProfile
from pipe4.domain.observation.models import LocationEvidenceType
from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import EpistemicStatus, VerificationStatus, VisibilityScope
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import StateValue
from pipe4.domain.policies.confidence import ConfidenceEngine
from pipe4.ports.authorization import AuthorizationPort
from pipe4.exceptions import PermissionDenied
from pipe4.ports.clock import Clock
from pipe4.ports.provenance import ProvenancePort, SourceRegistryPort

from .publication import PublicationService


class DeclarationService:
    def __init__(self, *, authorization: AuthorizationPort, provenance: ProvenancePort, sources: SourceRegistryPort, confidence: ConfidenceEngine, publication: PublicationService, clock: Clock) -> None:
        self.authorization=authorization; self.provenance=provenance; self.sources=sources; self.confidence=confidence; self.publication=publication; self.clock=clock

    async def declare(self, principal: Principal, *, identity: StateIdentity, value: StateValue, observed_at, source_id: str, visibility: VisibilityScope=VisibilityScope.PUBLIC, permission_tags: set[str] | None=None, idempotency_key: str | None=None):
        if not await self.authorization.can_declare(principal,entity_id=identity.entity_id): raise PermissionDenied('declaration authority required')
        now=self.clock.now(); source=await self.sources.get_source(source_id)
        if not source:
            source=SourceProfile(source_id=source_id,source_type='owner',authority_scopes={identity.state_type.value},reliability=0.75,evidence_capability=0.76)
            await self.sources.save_source(source)
        payload=f'{identity.key}:{value.model_dump_json()}:{observed_at.isoformat()}'.encode(); evidence=EvidenceRef(evidence_id=str(uuid4()),evidence_class=EvidenceClass.OWNER_DECLARATION,source_id=source_id,origin_key=f'owner:{source_id}',content_hash=hashlib.sha256(payload).hexdigest(),captured_at=observed_at,received_at=now)
        await self.provenance.save_evidence(evidence)
        breakdown=self.confidence.calculate(state_type=identity.state_type.value,sources=[source],evidence=[evidence],observed_at=observed_at,now=now,location_type=LocationEvidenceType.UNKNOWN)
        return await self.publication.publish(identity=identity,value=value,epistemic_status=EpistemicStatus.DECLARED,verification_status=VerificationStatus.UNVERIFIED,observed_at=observed_at,received_at=now,confidence=breakdown,source_ids=[source_id],evidence_ids=[evidence.evidence_id],visibility=visibility,permission_tags=permission_tags,idempotency_scope=f'declare:{principal.subject}',idempotency_key=idempotency_key)
