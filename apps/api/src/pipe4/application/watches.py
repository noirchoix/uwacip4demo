from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict

from pipe4.application.common import event
from pipe4.domain.principal import Principal
from pipe4.domain.state.models import StateVersion
from pipe4.domain.watch.models import WatchCondition, WatchProcess, WatchStatus, WatchSubscription
from pipe4.domain.policies.watch import evaluate_watch, watch_fingerprint
from pipe4.exceptions import NotFound, PermissionDenied
from pipe4.ports.authorization import AuthorizationPort
from pipe4.ports.clock import Clock
from pipe4.ports.notification import NotificationPort
from pipe4.repositories.protocols import EventRepository, WatchRepository


class WatchView(BaseModel):
    """Consumer-safe subscription plus its normalized condition.

    The shared process remains an implementation detail; exposing the condition lets mobile/web
    explain what the user is following without leaking any protected state value.
    """

    model_config = ConfigDict(extra="forbid")

    watch_id: str
    watch_process_id: str
    subscriber_subject: str
    status: WatchStatus
    condition: WatchCondition
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None


class WatchService:
    def __init__(self, *, repository: WatchRepository, authorization: AuthorizationPort, notifications: NotificationPort, events: EventRepository, clock: Clock) -> None:
        self.repository=repository;self.authorization=authorization;self.notifications=notifications;self.events=events;self.clock=clock

    async def _view(self, subscription: WatchSubscription) -> WatchView:
        process = await self.repository.get_process(subscription.watch_process_id)
        if not process:
            raise NotFound('watch process not found')
        return WatchView(
            watch_id=subscription.watch_id,
            watch_process_id=subscription.watch_process_id,
            subscriber_subject=subscription.subscriber_subject,
            status=subscription.status,
            condition=process.condition,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
            last_triggered_at=subscription.last_triggered_at,
        )

    async def create(self, principal: Principal, condition: WatchCondition) -> WatchSubscription:
        fp=watch_fingerprint(condition);process=await self.repository.get_process_by_fingerprint(fp)
        if not process:
            process=WatchProcess(fingerprint=fp,condition=condition,created_at=self.clock.now());await self.repository.save_process(process)
        now=self.clock.now();subscription=WatchSubscription(watch_process_id=process.watch_process_id,subscriber_subject=principal.subject,created_at=now,updated_at=now);await self.repository.save_subscription(subscription);return subscription

    async def create_view(self, principal: Principal, condition: WatchCondition) -> WatchView:
        return await self._view(await self.create(principal, condition))

    async def list(self, principal: Principal) -> list[WatchSubscription]:
        return await self.repository.list_subscriptions(principal.subject)

    async def list_views(self, principal: Principal) -> list[WatchView]:
        return [await self._view(item) for item in await self.list(principal)]

    async def get_view(self, principal: Principal, watch_id: str) -> WatchView:
        watch=await self.repository.get_subscription(watch_id)
        if not watch: raise NotFound('watch not found')
        if watch.subscriber_subject!=principal.subject: raise PermissionDenied('watch belongs to another subject')
        return await self._view(watch)

    async def set_paused(self, principal: Principal, watch_id: str, *, paused: bool) -> WatchSubscription:
        watch=await self.repository.get_subscription(watch_id)
        if not watch: raise NotFound('watch not found')
        if watch.subscriber_subject!=principal.subject: raise PermissionDenied('watch belongs to another subject')
        watch.status=WatchStatus.PAUSED if paused else WatchStatus.ACTIVE;watch.updated_at=self.clock.now();return await self.repository.save_subscription(watch)

    async def set_paused_view(self, principal: Principal, watch_id: str, *, paused: bool) -> WatchView:
        return await self._view(await self.set_paused(principal, watch_id, paused=paused))

    async def remove(self, principal: Principal, watch_id: str) -> None:
        watch=await self.repository.get_subscription(watch_id)
        if not watch: return
        if watch.subscriber_subject!=principal.subject: raise PermissionDenied('watch belongs to another subject')
        await self.repository.delete_subscription(watch_id)

    async def evaluate(self, state: StateVersion) -> int:
        triggered=0
        for subscription in await self.repository.subscriptions_for_identity(state.identity.key):
            if subscription.status==WatchStatus.PAUSED: continue
            process=await self.repository.get_process(subscription.watch_process_id)
            if not process: continue
            allowed=await self.authorization.can_view_subject(subscription.subscriber_subject,identity=state.identity,visibility=state.visibility,permission_tags=state.permission_tags)
            if not allowed: continue
            if evaluate_watch(process.condition.operator,state.value,process.condition.target):
                now=self.clock.now();subscription.status=WatchStatus.ALERTING;subscription.last_triggered_at=now;subscription.updated_at=now;await self.repository.save_subscription(subscription)
                await self.notifications.notify(subject=subscription.subscriber_subject,event_type='pipe4.watch.triggered',payload={'watch_id':subscription.watch_id,'state_version_id':state.state_version_id,'triggered_at':now.isoformat(),'observed_at':state.observed_at.isoformat()})
                await self.events.append_event(event('watch.triggered',aggregate_type='watch_subscription',aggregate_id=subscription.watch_id,occurred_at=now,payload={'state_version_id':state.state_version_id,'observed_at':state.observed_at.isoformat()}));triggered+=1
        return triggered
