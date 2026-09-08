from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Mapping

from pipe4.domain.acquisition.models import AcquisitionAttempt, AcquisitionAttemptStatus, AcquisitionJobStatus, GapReason, StateRequestStatus
from pipe4.domain.evidence.models import EvidenceClass, EvidenceRef
from pipe4.domain.observation.models import ObservationRecord, ObservationStatus
from pipe4.domain.principal import Principal
from pipe4.exceptions import ExternalDependencyUnavailable
from pipe4.ports.acquisition import AcquisitionSourcePort
from pipe4.ports.clock import Clock
from pipe4.ports.evidence_store import EvidenceStorePort
from pipe4.ports.provenance import ProvenancePort, SourceRegistryPort
from pipe4.repositories.protocols import AcquisitionRepository, ObservationRepository, RequestRepository

from .verification import VerificationService


class AcquisitionService:
    def __init__(self, *, acquisition: AcquisitionRepository, requests: RequestRepository, observations: ObservationRepository, sources: SourceRegistryPort, connectors: Mapping[str, AcquisitionSourcePort], provenance: ProvenancePort, evidence_store: EvidenceStorePort | None, verification: VerificationService, clock: Clock) -> None:
        self.acquisition=acquisition;self.requests=requests;self.observations=observations;self.sources=sources;self.connectors=connectors;self.provenance=provenance;self.evidence_store=evidence_store;self.verification=verification;self.clock=clock

    async def run_job(self, job_id: str):
        job=await self.acquisition.get_job(job_id)
        if not job: raise KeyError(job_id)
        request=await self.requests.get_request(job.request_id)
        if not request: raise KeyError(job.request_id)
        now=self.clock.now()
        if now>=job.deadline_at:
            job.status=AcquisitionJobStatus.TIMED_OUT;job.updated_at=now;await self.acquisition.save_job(job);request.status=StateRequestStatus.TIMED_OUT;request.gap_reason=GapReason.UNKNOWN;request.updated_at=now;await self.requests.save_request(request);return None
        job.status=AcquisitionJobStatus.IN_PROGRESS;job.updated_at=now;await self.acquisition.save_job(job)
        for source_id in job.candidate_source_ids:
            source=await self.sources.get_source_for_context(source_id,entity_id=job.identity.entity_id,state_type=job.identity.state_type);provider=source.provider_key if source else None;connector=self.connectors.get(provider or '')
            attempt=AcquisitionAttempt(job_id=job.job_id,source_id=source_id,started_at=self.clock.now());await self.acquisition.save_attempt(attempt)
            if not connector:
                attempt.status=AcquisitionAttemptStatus.INADMISSIBLE;attempt.reason='no configured connector';attempt.completed_at=self.clock.now();await self.acquisition.save_attempt(attempt);continue
            try:
                result=await connector.acquire(identity=job.identity,decision_context=job.decision_context)
                captured=datetime.fromisoformat(result.observed_at_iso.replace('Z','+00:00'));received=self.clock.now();object_ref=None;content_hash=hashlib.sha256(f'{source_id}:{result.value.model_dump_json()}:{result.observed_at_iso}'.encode()).hexdigest()
                if result.evidence_payload is not None and self.evidence_store:
                    stored=await self.evidence_store.put_bytes(data=result.evidence_payload,content_type=result.evidence_content_type or 'application/octet-stream',suggested_name='acquisition-evidence');object_ref=stored.object_ref;content_hash=stored.content_hash
                evidence=EvidenceRef(evidence_id=hashlib.sha256(f'{job.job_id}:{source_id}:{content_hash}'.encode()).hexdigest()[:36],evidence_class=EvidenceClass.INSTITUTIONAL_API,source_id=source_id,origin_key=result.origin_key,content_hash=content_hash,captured_at=captured,received_at=received,object_ref=object_ref);await self.provenance.save_evidence(evidence)
                observation=ObservationRecord(identity=job.identity,proposed_value=result.value,source_id=source_id,actor_subject=None,epistemic_status=result.epistemic_status,status=ObservationStatus.VERIFYING,observed_at=captured,received_at=received,latitude=result.latitude,longitude=result.longitude,location_accuracy_m=result.location_accuracy_m,location_evidence_type=result.location_type,evidence_ids=[evidence.evidence_id]);await self.observations.save_observation(observation)
                attempt.status=AcquisitionAttemptStatus.SUCCEEDED;attempt.completed_at=self.clock.now();attempt.result_observation_id=observation.observation_id;await self.acquisition.save_attempt(attempt);state=await self.verification.verify_observation(observation.observation_id)
                if state:
                    job.status=AcquisitionJobStatus.SUCCEEDED;job.updated_at=self.clock.now();await self.acquisition.save_job(job);request.status=StateRequestStatus.RESOLVED;request.resolved_state_version_id=state.state_version_id;request.updated_at=self.clock.now();await self.requests.save_request(request);return state
            except Exception as exc:
                attempt.status=AcquisitionAttemptStatus.FAILED;attempt.completed_at=self.clock.now();attempt.reason=str(exc)[:500];await self.acquisition.save_attempt(attempt)
        job.status=AcquisitionJobStatus.FAILED;job.updated_at=self.clock.now();await self.acquisition.save_job(job);request.status=StateRequestStatus.UNKNOWN;request.gap_reason=GapReason.UNKNOWN;request.updated_at=self.clock.now();await self.requests.save_request(request);return None
