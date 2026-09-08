from __future__ import annotations

from pipe4.application.common import event
from pipe4.domain.access.models import AccessRequest, AccessRequestStatus, PermissionGrant
from pipe4.domain.principal import Principal
from pipe4.exceptions import Conflict, NotFound, PermissionDenied
from pipe4.ports.authorization import AuthorizationPort
from pipe4.ports.clock import Clock
from pipe4.repositories.protocols import AccessRepository, EventRepository


class AccessService:
    def __init__(self, *, repository: AccessRepository, authorization: AuthorizationPort, events: EventRepository, clock: Clock) -> None:
        self.repository=repository;self.authorization=authorization;self.events=events;self.clock=clock

    async def request(self, principal: Principal, *, entity_id: str, identity_key: str | None=None, permission: str='READ', scope: dict | None=None) -> AccessRequest:
        now=self.clock.now(); request=AccessRequest(requester_subject=principal.subject,target_entity_id=entity_id,target_identity_key=identity_key,requested_permission=permission,requested_scope=scope or {},requested_at=now)
        await self.repository.save_access_request(request);await self.events.append_event(event('access.requested',aggregate_type='access_request',aggregate_id=request.access_request_id,occurred_at=now,payload={'entity_id':entity_id,'status':request.status.value}));return request

    async def decide(self, principal: Principal, request_id: str, *, approve: bool, reason: str | None=None, expires_at=None) -> AccessRequest:
        request=await self.repository.get_access_request(request_id)
        if not request: raise NotFound('access request not found')
        if not await self.authorization.can_decide_access(principal,entity_id=request.target_entity_id): raise PermissionDenied('access decision authority required')
        if request.status!=AccessRequestStatus.PENDING: raise Conflict('only pending access requests may be decided')
        now=self.clock.now();request.status=AccessRequestStatus.APPROVED if approve else AccessRequestStatus.DENIED;request.decided_at=now;request.decided_by_subject=principal.subject;request.decision_reason=reason;request.expires_at=expires_at;await self.repository.save_access_request(request)
        if approve:
            await self.repository.save_grant(PermissionGrant(access_request_id=request.access_request_id,subject=request.requester_subject,target_entity_id=request.target_entity_id,target_identity_key=request.target_identity_key,permission=request.requested_permission,scope=request.requested_scope,created_at=now,expires_at=expires_at))
        await self.events.append_event(event('access.decided',aggregate_type='access_request',aggregate_id=request.access_request_id,occurred_at=now,payload={'status':request.status.value}));return request

    async def revoke(self, principal: Principal, request_id: str, *, reason: str | None=None) -> AccessRequest:
        request=await self.repository.get_access_request(request_id)
        if not request: raise NotFound('access request not found')
        if not await self.authorization.can_decide_access(principal,entity_id=request.target_entity_id): raise PermissionDenied('access revocation authority required')
        if request.status!=AccessRequestStatus.APPROVED: raise Conflict('only approved access may be revoked')
        now=self.clock.now();request.status=AccessRequestStatus.REVOKED;request.decision_reason=reason;request.decided_at=now;request.decided_by_subject=principal.subject;await self.repository.save_access_request(request);await self.repository.revoke_grant(request.access_request_id,revoked_at=now);await self.events.append_event(event('access.revoked',aggregate_type='access_request',aggregate_id=request.access_request_id,occurred_at=now));return request

    async def cancel(self, principal: Principal, request_id: str) -> AccessRequest:
        request=await self.repository.get_access_request(request_id)
        if not request: raise NotFound('access request not found')
        if request.requester_subject!=principal.subject: raise PermissionDenied('only requester may cancel')
        if request.status!=AccessRequestStatus.PENDING: raise Conflict('only pending requests may be cancelled')
        request.status=AccessRequestStatus.CANCELLED;request.decided_at=self.clock.now();await self.repository.save_access_request(request);return request

    async def list(self, principal: Principal) -> list[AccessRequest]:
        return await self.repository.list_access_requests(principal.subject)
