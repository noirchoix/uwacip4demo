from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Iterable

from pipe4.domain.access.models import AccessRequest, AccessRequestStatus, PermissionGrant
from pipe4.domain.acquisition.models import (
    AcquisitionAttempt,
    AcquisitionJob,
    AcquisitionJobStatus,
    StateRequest,
    StateRequestStatus,
    TargetedAcquisitionRequest,
)
from pipe4.domain.contradiction import ContradictionRecord, ContradictionStatus
from pipe4.domain.entities.models import ReferenceEntity
from pipe4.domain.events.models import DomainEvent, OutboxRecord
from pipe4.domain.observation.models import ObservationRecord
from pipe4.domain.state.enums import PublishedStateLifecycle
from pipe4.domain.state.models import CurrentStateProjection, StateVersion
from pipe4.domain.watch.models import WatchProcess, WatchStatus, WatchSubscription
from pipe4.exceptions import Conflict, NotFound


class InMemoryRepositories:
    """Test/reference adapter implementing the repository ports with process-local state."""

    def __init__(self) -> None:
        self.states: dict[str, StateVersion] = {}
        self.current_projection: dict[str, CurrentStateProjection] = {}
        self.observations: dict[str, ObservationRecord] = {}
        self.requests: dict[str, StateRequest] = {}
        self.jobs: dict[str, AcquisitionJob] = {}
        self.attempts: dict[str, AcquisitionAttempt] = {}
        self.watch_processes: dict[str, WatchProcess] = {}
        self.watch_subscriptions: dict[str, WatchSubscription] = {}
        self.access_requests: dict[str, AccessRequest] = {}
        self.grants: dict[str, PermissionGrant] = {}
        self.entities: dict[str, ReferenceEntity] = {}
        self.targeted: dict[str, TargetedAcquisitionRequest] = {}
        self.contradictions: dict[str, ContradictionRecord] = {}
        self.events: list[DomainEvent] = []
        self.outbox: dict[str, OutboxRecord] = {}
        self.idempotency: dict[tuple[str, str], str] = {}
        self._publication_locks: dict[str, asyncio.Lock] = {}

    def _lock(self, identity_key: str) -> asyncio.Lock:
        return self._publication_locks.setdefault(identity_key, asyncio.Lock())

    async def current(self, identity_key: str) -> StateVersion | None:
        projection = self.current_projection.get(identity_key)
        return self.states.get(projection.state_version_id) if projection else None

    async def get_version(self, state_version_id: str) -> StateVersion | None:
        return self.states.get(state_version_id)

    async def history(self, identity_key: str, *, limit: int = 50) -> list[StateVersion]:
        rows = [state for state in self.states.values() if state.identity.key == identity_key]
        rows.sort(key=lambda row: (row.version, row.created_at), reverse=True)
        return rows[:limit]

    async def list_current(self) -> list[StateVersion]:
        return [
            self.states[p.state_version_id]
            for p in self.current_projection.values()
            if p.state_version_id in self.states
        ]

    async def publish_state(
        self,
        state: StateVersion,
        *,
        events: list[DomainEvent],
        idempotency_scope: str | None = None,
        idempotency_key: str | None = None,
    ) -> StateVersion:
        async with self._lock(state.identity.key):
            if idempotency_scope and idempotency_key:
                existing_id = self.idempotency.get((idempotency_scope, idempotency_key))
                if existing_id:
                    existing = self.states.get(existing_id)
                    if existing:
                        return existing

            incumbent = await self.current(state.identity.key)
            if incumbent:
                incumbent.lifecycle_status = PublishedStateLifecycle.REPLACED
                self.states[incumbent.state_version_id] = incumbent
                state.predecessor_state_version_id = incumbent.state_version_id
                state.version = incumbent.version + 1
            else:
                state.version = 1

            self.states[state.state_version_id] = state
            self.current_projection[state.identity.key] = CurrentStateProjection(
                identity_key=state.identity.key,
                state_version_id=state.state_version_id,
                updated_at=state.created_at,
            )
            for event in events:
                self.events.append(event)
                out = OutboxRecord(event=event, created_at=event.occurred_at)
                self.outbox[out.outbox_id] = out
            if idempotency_scope and idempotency_key:
                self.idempotency[(idempotency_scope, idempotency_key)] = state.state_version_id
            return state

    async def expire_state(self, state_version_id: str, *, event: DomainEvent) -> StateVersion:
        state = self.states.get(state_version_id)
        if not state:
            raise NotFound("state version not found")
        if state.lifecycle_status == PublishedStateLifecycle.REPLACED:
            raise Conflict("replaced state cannot be expired as current state")
        state.lifecycle_status = PublishedStateLifecycle.EXPIRED
        self.states[state_version_id] = state
        self.events.append(event)
        out = OutboxRecord(event=event, created_at=event.occurred_at)
        self.outbox[out.outbox_id] = out
        return state

    async def save_observation(self, observation: ObservationRecord) -> ObservationRecord:
        self.observations[observation.observation_id] = observation
        return observation

    async def get_observation(self, observation_id: str) -> ObservationRecord | None:
        return self.observations.get(observation_id)

    async def update_observation(self, observation: ObservationRecord) -> ObservationRecord:
        self.observations[observation.observation_id] = observation
        return observation

    async def find_active_request(self, fingerprint: str) -> StateRequest | None:
        active = {
            StateRequestStatus.REQUESTED,
            StateRequestStatus.ACQUIRING,
            StateRequestStatus.VERIFYING,
        }
        for request in self.requests.values():
            if request.fingerprint == fingerprint and request.status in active:
                return request
        return None

    async def save_request(self, request: StateRequest) -> StateRequest:
        self.requests[request.request_id] = request
        return request

    async def get_request(self, request_id: str) -> StateRequest | None:
        return self.requests.get(request_id)

    async def active_demand_count(self, identity_key: str) -> int:
        return sum(
            req.demand_count
            for req in self.requests.values()
            if req.identity.key == identity_key
            and req.status in {
                StateRequestStatus.REQUESTED,
                StateRequestStatus.ACQUIRING,
                StateRequestStatus.VERIFYING,
            }
        )

    async def save_job(self, job: AcquisitionJob) -> AcquisitionJob:
        self.jobs[job.job_id] = job
        return job

    async def get_job(self, job_id: str) -> AcquisitionJob | None:
        return self.jobs.get(job_id)

    async def pending_jobs(self, *, limit: int = 100) -> list[AcquisitionJob]:
        rows = [
            job for job in self.jobs.values()
            if job.status in {AcquisitionJobStatus.PENDING, AcquisitionJobStatus.IN_PROGRESS}
        ]
        rows.sort(key=lambda item: item.created_at)
        return rows[:limit]

    async def save_attempt(self, attempt: AcquisitionAttempt) -> AcquisitionAttempt:
        self.attempts[attempt.attempt_id] = attempt
        return attempt

    async def attempts_for_job(self, job_id: str) -> list[AcquisitionAttempt]:
        return [attempt for attempt in self.attempts.values() if attempt.job_id == job_id]

    async def get_process_by_fingerprint(self, fingerprint: str) -> WatchProcess | None:
        return next(
            (p for p in self.watch_processes.values() if p.fingerprint == fingerprint),
            None,
        )

    async def get_process(self, watch_process_id: str) -> WatchProcess | None:
        return self.watch_processes.get(watch_process_id)

    async def save_process(self, process: WatchProcess) -> WatchProcess:
        self.watch_processes[process.watch_process_id] = process
        return process

    async def save_subscription(self, subscription: WatchSubscription) -> WatchSubscription:
        self.watch_subscriptions[subscription.watch_id] = subscription
        return subscription

    async def get_subscription(self, watch_id: str) -> WatchSubscription | None:
        return self.watch_subscriptions.get(watch_id)

    async def list_subscriptions(self, subject: str) -> list[WatchSubscription]:
        return [
            watch for watch in self.watch_subscriptions.values()
            if watch.subscriber_subject == subject
        ]

    async def subscriptions_for_identity(self, identity_key: str) -> list[WatchSubscription]:
        result: list[WatchSubscription] = []
        for subscription in self.watch_subscriptions.values():
            process = self.watch_processes.get(subscription.watch_process_id)
            if process and process.condition.identity.key == identity_key:
                result.append(subscription)
        return result

    async def delete_subscription(self, watch_id: str) -> None:
        self.watch_subscriptions.pop(watch_id, None)

    async def active_watch_count(self, identity_key: str) -> int:
        return sum(
            1
            for subscription in await self.subscriptions_for_identity(identity_key)
            if subscription.status != WatchStatus.PAUSED
        )

    async def save_access_request(self, request: AccessRequest) -> AccessRequest:
        self.access_requests[request.access_request_id] = request
        return request

    async def get_access_request(self, request_id: str) -> AccessRequest | None:
        return self.access_requests.get(request_id)

    async def list_access_requests(self, subject: str) -> list[AccessRequest]:
        return [
            request for request in self.access_requests.values()
            if request.requester_subject == subject
        ]

    async def save_grant(self, grant: PermissionGrant) -> PermissionGrant:
        self.grants[grant.grant_id] = grant
        return grant

    async def has_grant(
        self, *, subject: str, entity_id: str, identity_key: str | None, permission: str
    ) -> bool:
        now = datetime.now().astimezone()
        for grant in self.grants.values():
            if (
                grant.subject == subject
                and grant.target_entity_id == entity_id
                and grant.permission == permission
                and grant.revoked_at is None
                and (grant.expires_at is None or grant.expires_at > now)
                and (grant.target_identity_key is None or grant.target_identity_key == identity_key)
            ):
                return True
        return False

    async def revoke_grant(self, access_request_id: str, *, revoked_at: datetime) -> None:
        for grant in self.grants.values():
            if grant.access_request_id == access_request_id and grant.revoked_at is None:
                grant.revoked_at = revoked_at

    async def pending_request_status(
        self, *, subject: str, entity_id: str, identity_key: str | None
    ) -> str | None:
        candidates = [
            request
            for request in self.access_requests.values()
            if request.requester_subject == subject
            and request.target_entity_id == entity_id
            and (request.target_identity_key is None or request.target_identity_key == identity_key)
            and request.status == AccessRequestStatus.PENDING
        ]
        return candidates[-1].status.value if candidates else None

    async def save_entity(self, entity: ReferenceEntity) -> ReferenceEntity:
        self.entities[entity.entity_id] = entity
        return entity

    async def get_entity(self, entity_id: str) -> ReferenceEntity | None:
        return self.entities.get(entity_id)

    async def list_entities(self) -> list[ReferenceEntity]:
        return list(self.entities.values())

    async def save_targeted(self, request: TargetedAcquisitionRequest) -> TargetedAcquisitionRequest:
        self.targeted[request.targeted_request_id] = request
        return request

    async def get_targeted(self, request_id: str) -> TargetedAcquisitionRequest | None:
        return self.targeted.get(request_id)

    async def list_targeted_for_subject(self, subject: str) -> list[TargetedAcquisitionRequest]:
        return [request for request in self.targeted.values() if request.target_subject == subject]

    async def save_contradiction(self, contradiction: ContradictionRecord) -> ContradictionRecord:
        self.contradictions[contradiction.contradiction_id] = contradiction
        return contradiction

    async def open_for_identity(self, identity_key: str) -> list[ContradictionRecord]:
        return [
            row for row in self.contradictions.values()
            if row.identity_key == identity_key and row.status == ContradictionStatus.OPEN
        ]

    async def append_event(self, event: DomainEvent) -> None:
        self.events.append(event)
        out = OutboxRecord(event=event, created_at=event.occurred_at)
        self.outbox[out.outbox_id] = out

    async def append_events(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.append_event(event)

    async def list_events(self, *, limit: int = 200) -> list[DomainEvent]:
        return self.events[-limit:]

    async def pending_outbox(self, *, limit: int = 100) -> list[OutboxRecord]:
        rows = [row for row in self.outbox.values() if row.published_at is None]
        rows.sort(key=lambda item: item.created_at)
        return rows[:limit]

    async def mark_outbox_published(self, outbox_id: str, *, published_at: datetime) -> None:
        if row := self.outbox.get(outbox_id):
            row.published_at = published_at

    async def mark_outbox_failed(self, outbox_id: str, *, error: str) -> None:
        if row := self.outbox.get(outbox_id):
            row.attempts += 1
            row.last_error = error
