from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from pydantic import BaseModel, ConfigDict

from pipe4.application.common import event
from pipe4.domain.acquisition.models import TargetedAcquisitionRequest, TargetedAcquisitionStatus
from pipe4.domain.principal import Principal
from pipe4.domain.state.identity import StateIdentity
from pipe4.exceptions import Conflict, NotFound, PermissionDenied
from pipe4.ports.clock import Clock
from pipe4.repositories.protocols import EventRepository, RequestRepository, TargetedAcquisitionRepository


class TargetedAcquisitionView(BaseModel):
    model_config = ConfigDict(extra='forbid')

    targeted_request_id: str
    state_request_id: str
    target_subject: str
    status: TargetedAcquisitionStatus
    offered_at: datetime
    expires_at: datetime
    accepted_at: datetime | None = None
    completed_observation_id: str | None = None
    reward_label: str | None = None
    identity: StateIdentity | None = None
    what_to_confirm: str | None = None


class TargetedAcquisitionService:
    def __init__(self, *, repository: TargetedAcquisitionRepository, state_requests: RequestRepository, events: EventRepository, clock: Clock) -> None:
        self.repository=repository;self.state_requests=state_requests;self.events=events;self.clock=clock

    async def _view(self, request: TargetedAcquisitionRequest) -> TargetedAcquisitionView:
        state_request=await self.state_requests.get_request(request.state_request_id)
        identity=state_request.identity if state_request else None
        description=None
        if identity:
            description=f"Confirm {identity.state_type.value.lower()} for {identity.object_key}"
        return TargetedAcquisitionView(**request.model_dump(),identity=identity,what_to_confirm=description)

    async def offer(self, *, state_request_id: str, target_subject: str, ttl_seconds: int=900, reward_label: str | None=None) -> TargetedAcquisitionRequest:
        now=self.clock.now();request=TargetedAcquisitionRequest(state_request_id=state_request_id,target_subject=target_subject,offered_at=now,expires_at=now+timedelta(seconds=ttl_seconds),reward_label=reward_label);await self.repository.save_targeted(request);await self.events.append_event(event('targeted_acquisition.offered',aggregate_type='targeted_acquisition',aggregate_id=request.targeted_request_id,occurred_at=now));return request

    async def offer_view(self, **kwargs) -> TargetedAcquisitionView:
        return await self._view(await self.offer(**kwargs))

    async def list(self, principal: Principal) -> list[TargetedAcquisitionRequest]:
        return await self.repository.list_targeted_for_subject(principal.subject)

    async def list_views(self, principal: Principal) -> list[TargetedAcquisitionView]:
        return [await self._view(item) for item in await self.list(principal)]

    async def get_view(self, principal: Principal, request_id: str) -> TargetedAcquisitionView:
        result=await self.repository.get_targeted(request_id)
        if not result: raise NotFound('targeted acquisition request not found')
        if result.target_subject!=principal.subject: raise PermissionDenied('targeted request belongs to another subject')
        return await self._view(result)

    async def respond(self, principal: Principal, request_id: str, *, accept: bool) -> TargetedAcquisitionRequest:
        request=await self.repository.get_targeted(request_id)
        if not request: raise NotFound('targeted acquisition request not found')
        if request.target_subject!=principal.subject: raise PermissionDenied('targeted request belongs to another subject')
        if request.status!=TargetedAcquisitionStatus.OFFERED: raise Conflict('targeted acquisition request is not open')
        now=self.clock.now()
        if now>=request.expires_at: request.status=TargetedAcquisitionStatus.EXPIRED
        else: request.status=TargetedAcquisitionStatus.ACCEPTED if accept else TargetedAcquisitionStatus.DECLINED;request.accepted_at=now if accept else None
        await self.repository.save_targeted(request);return request

    async def respond_view(self, principal: Principal, request_id: str, *, accept: bool) -> TargetedAcquisitionView:
        return await self._view(await self.respond(principal,request_id,accept=accept))

    async def complete(self, principal: Principal, request_id: str, *, observation_id: str) -> TargetedAcquisitionView:
        request=await self.repository.get_targeted(request_id)
        if not request: raise NotFound('targeted acquisition request not found')
        if request.target_subject!=principal.subject: raise PermissionDenied('targeted request belongs to another subject')
        if request.status not in {TargetedAcquisitionStatus.ACCEPTED,TargetedAcquisitionStatus.COMPLETED}:
            raise Conflict('targeted acquisition request must be accepted before completion')
        if request.completed_observation_id and request.completed_observation_id != observation_id:
            raise Conflict('targeted acquisition request is already linked to another observation')
        request.status=TargetedAcquisitionStatus.COMPLETED
        request.completed_observation_id=observation_id
        await self.repository.save_targeted(request)
        await self.events.append_event(event('targeted_acquisition.completed',aggregate_type='targeted_acquisition',aggregate_id=request.targeted_request_id,occurred_at=self.clock.now(),payload={'observation_id':observation_id}))
        return await self._view(request)
