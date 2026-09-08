from __future__ import annotations

from pipe4.application.common import event
from pipe4.domain.contradiction import ContradictionRecord
from pipe4.domain.observation.models import ObservationStatus
from pipe4.domain.policies.confidence import ConfidenceEngine
from pipe4.domain.policies.contradiction import ContradictionEngine
from pipe4.domain.policies.registry import PolicyRegistry
from pipe4.domain.policies.verification import VerificationPolicy
from pipe4.domain.state.enums import EpistemicStatus, PublishedStateLifecycle, VerificationStatus
from pipe4.ports.clock import Clock
from pipe4.ports.provenance import ProvenancePort, SourceRegistryPort
from pipe4.repositories.protocols import ContradictionRepository, EventRepository, ObservationRepository, StateRepository

from .publication import PublicationService


class VerificationService:
    def __init__(self, *, observations: ObservationRepository, states: StateRepository, contradictions: ContradictionRepository, provenance: ProvenancePort, sources: SourceRegistryPort, confidence: ConfidenceEngine, verification: VerificationPolicy, contradiction_engine: ContradictionEngine, publication: PublicationService, events: EventRepository, policies: PolicyRegistry, clock: Clock) -> None:
        self.observations=observations;self.states=states;self.contradictions=contradictions;self.provenance=provenance;self.sources=sources;self.confidence=confidence;self.verification=verification;self.contradiction_engine=contradiction_engine;self.publication=publication;self.events=events;self.policies=policies;self.clock=clock

    async def verify_observation(self, observation_id: str):
        observation=await self.observations.get_observation(observation_id)
        if not observation: raise KeyError(observation_id)
        evidence=await self.provenance.get_evidence(observation.evidence_ids)
        source=await self.sources.get_source_for_context(observation.source_id,entity_id=observation.identity.entity_id,state_type=observation.identity.state_type); sources=[source] if source else []
        incumbent=await self.states.current(observation.identity.key)
        breakdown=self.confidence.calculate(state_type=observation.identity.state_type.value,sources=sources,evidence=evidence,observed_at=observation.observed_at,now=self.clock.now(),location_type=observation.location_evidence_type)
        contradiction=False
        if incumbent:
            state_policy=self.policies.state_type(observation.identity.state_type)
            assessment=self.contradiction_engine.assess(incumbent=incumbent,observation=observation,equivalence_seconds=state_policy.material_equivalence_seconds)
            contradiction=assessment.material and breakdown.weighted_score >= state_policy.contradiction_minimum_confidence
            if contradiction:
                record=ContradictionRecord(identity_key=observation.identity.key,incumbent_state_version_id=incumbent.state_version_id,competing_observation_id=observation.observation_id,reason=assessment.reason,created_at=self.clock.now())
                await self.contradictions.save_contradiction(record)
        decision=self.verification.evaluate(state_type=observation.identity.state_type.value,epistemic_status=observation.epistemic_status,confidence=breakdown,evidence=evidence,has_unresolved_material_contradiction=contradiction)
        if contradiction and incumbent:
            disputed=await self.publication.publish(identity=incumbent.identity,value=incumbent.value,epistemic_status=incumbent.epistemic_status,verification_status=VerificationStatus.INCONCLUSIVE,observed_at=max(incumbent.observed_at,observation.observed_at),received_at=self.clock.now(),confidence=breakdown,source_ids=list(dict.fromkeys([*incumbent.source_ids,observation.source_id])),evidence_ids=list(dict.fromkeys([*incumbent.evidence_ids,*observation.evidence_ids])),visibility=incumbent.visibility,permission_tags=incumbent.permission_tags,lifecycle_status=PublishedStateLifecycle.DISPUTED)
            observation.status=ObservationStatus.CONSUMED;observation.consumed_state_version_id=disputed.state_version_id;await self.observations.update_observation(observation)
            return disputed
        if decision.status==VerificationStatus.VERIFIED:
            state=await self.publication.publish(identity=observation.identity,value=observation.proposed_value,epistemic_status=EpistemicStatus.VERIFIED,verification_status=VerificationStatus.VERIFIED,observed_at=observation.observed_at,received_at=observation.received_at,confidence=breakdown,source_ids=[observation.source_id],evidence_ids=observation.evidence_ids,last_verified_at=self.clock.now())
            observation.status=ObservationStatus.CONSUMED;observation.consumed_state_version_id=state.state_version_id;await self.observations.update_observation(observation)
            return state
        observation.status=ObservationStatus.VERIFYING;await self.observations.update_observation(observation)
        await self.events.append_event(event('observation.verification_pending',aggregate_type='observation',aggregate_id=observation.observation_id,occurred_at=self.clock.now(),payload={'reason':decision.reason}))
        return None
