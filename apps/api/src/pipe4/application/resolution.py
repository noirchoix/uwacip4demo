from __future__ import annotations

from datetime import timedelta

from pipe4.application.common import event, fingerprint
from pipe4.domain.acquisition.models import AcquisitionJob, DecisionContext, GapReason, StateRequest, StateRequestStatus
from pipe4.domain.principal import Principal
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.policies.source_ranking import SourceRankingEngine
from pipe4.ports.clock import Clock
from pipe4.ports.jobs import JobSchedulerPort
from pipe4.ports.provenance import SourceRegistryPort
from pipe4.repositories.protocols import AcquisitionRepository, EventRepository, RequestRepository


class ResolutionService:
    def __init__(self, *, requests: RequestRepository, acquisition: AcquisitionRepository, sources: SourceRegistryPort, ranking: SourceRankingEngine, events: EventRepository, clock: Clock, jobs: JobSchedulerPort | None=None) -> None:
        self.requests=requests; self.acquisition=acquisition; self.sources=sources; self.ranking=ranking; self.events=events; self.clock=clock; self.jobs=jobs

    async def request(self, principal: Principal, *, identity: StateIdentity, decision_context: DecisionContext, reason: GapReason) -> StateRequest:
        now=self.clock.now(); fp=fingerprint({'identity_key':identity.key,'decision_context':decision_context.model_dump(mode='json')})
        existing=await self.requests.find_active_request(fp)
        if existing:
            existing.demand_count += 1; existing.updated_at=now; return await self.requests.save_request(existing)
        request=StateRequest(identity=identity,requester_subject=principal.subject,decision_context=decision_context,gap_reason=reason,fingerprint=fp,created_at=now,updated_at=now)
        await self.requests.save_request(request)
        ranked=self.ranking.rank(await self.sources.list_sources_for_context(entity_id=identity.entity_id,state_type=identity.state_type),state_type=identity.state_type)
        if ranked:
            request.status=StateRequestStatus.ACQUIRING; request.updated_at=now; await self.requests.save_request(request)
            job=AcquisitionJob(request_id=request.request_id,identity=identity,decision_context=decision_context,candidate_source_ids=[r.source.source_id for r in ranked],idempotency_key=f'acquire:{fp}',created_at=now,updated_at=now,deadline_at=now+timedelta(seconds=60))
            await self.acquisition.save_job(job)
            if self.jobs: await self.jobs.enqueue_acquisition(job.job_id)
        await self.events.append_event(event('reality_gap.created',aggregate_type='state_request',aggregate_id=request.request_id,occurred_at=now,payload={'identity_key':identity.key,'gap_reason':reason.value,'candidate_count':len(ranked)}))
        return request

    async def get_request(self, request_id: str) -> StateRequest | None:
        return await self.requests.get_request(request_id)

    async def mark_unknown(self, request_id: str, *, reason: GapReason=GapReason.UNKNOWN) -> StateRequest:
        request=await self.requests.get_request(request_id)
        if not request: raise KeyError(request_id)
        request.status=StateRequestStatus.UNKNOWN; request.gap_reason=reason; request.updated_at=self.clock.now(); await self.requests.save_request(request)
        await self.events.append_event(event('state_resolution.unknown',aggregate_type='state_request',aggregate_id=request.request_id,occurred_at=request.updated_at,payload={'identity_key':request.identity.key,'reason':reason.value}))
        return request
