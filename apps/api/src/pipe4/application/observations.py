from __future__ import annotations

import hashlib
from uuid import uuid4

from pipe4.application.common import event
from pipe4.domain.evidence.models import EvidenceClass, EvidenceRef, SourceProfile
from pipe4.domain.observation.models import LocationEvidenceType, ObservationRecord, ObservationStatus
from pipe4.domain.principal import Principal
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import StateValue
from pipe4.ports.clock import Clock
from pipe4.ports.jobs import JobSchedulerPort
from pipe4.ports.provenance import ProvenancePort, SourceRegistryPort
from pipe4.repositories.protocols import EventRepository, ObservationRepository


class ObservationService:
    def __init__(self, *, observations: ObservationRepository, provenance: ProvenancePort, sources: SourceRegistryPort, events: EventRepository, clock: Clock, jobs: JobSchedulerPort | None=None) -> None:
        self.observations=observations; self.provenance=provenance; self.sources=sources; self.events=events; self.clock=clock; self.jobs=jobs

    @staticmethod
    def witness_source_id(subject: str) -> str:
        return 'witness:'+hashlib.sha256(subject.encode()).hexdigest()[:24]

    async def submit(self, principal: Principal, *, identity: StateIdentity, value: StateValue, observed_at, source_id: str | None=None, latitude: float | None=None, longitude: float | None=None, location_accuracy_m: float | None=None, location_description: str | None=None, original_input_ref: str | None=None, interpretation_confidence: float | None=None, evidence_class: EvidenceClass=EvidenceClass.WITNESS_REPORT, evidence_object_ref: str | None=None, evidence_content_hash: str | None=None) -> ObservationRecord:
        now=self.clock.now(); sid=source_id or self.witness_source_id(principal.subject); source=await self.sources.get_source(sid)
        if not source:
            source=SourceProfile(source_id=sid,source_type='witness',authority_scopes=set(),reliability=0.55,evidence_capability=0.62); await self.sources.save_source(source)
        if latitude is not None and longitude is not None: location_type=LocationEvidenceType.GPS_CONFIRMED
        elif location_description: location_type=LocationEvidenceType.MANUALLY_DESCRIBED
        else: location_type=LocationEvidenceType.UNKNOWN
        raw=(original_input_ref or value.model_dump_json()).encode(); evidence=EvidenceRef(evidence_id=str(uuid4()),evidence_class=evidence_class,source_id=sid,origin_key=f'{sid}:{observed_at.date().isoformat()}',content_hash=evidence_content_hash or hashlib.sha256(raw).hexdigest(),captured_at=observed_at,received_at=now,object_ref=evidence_object_ref)
        await self.provenance.save_evidence(evidence)
        observation=ObservationRecord(identity=identity,proposed_value=value,source_id=sid,actor_subject=principal.subject,status=ObservationStatus.VERIFYING,observed_at=observed_at,received_at=now,latitude=latitude,longitude=longitude,location_accuracy_m=location_accuracy_m,location_description=location_description,location_evidence_type=location_type,evidence_ids=[evidence.evidence_id],original_input_ref=original_input_ref,interpretation_confidence=interpretation_confidence)
        await self.observations.save_observation(observation); await self.events.append_event(event('observation.received',aggregate_type='observation',aggregate_id=observation.observation_id,occurred_at=now,payload={'identity_key':identity.key,'state_type':identity.state_type.value}))
        if self.jobs: await self.jobs.enqueue_verification(observation.observation_id)
        return observation
