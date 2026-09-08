from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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
from pipe4.domain.state.models import StateVersion
from pipe4.domain.watch.models import WatchProcess, WatchStatus, WatchSubscription
from pipe4.exceptions import Conflict, NotFound

from . import models as db
from .codec import row_to_state, state_to_row


def _model_dump(value) -> dict:
    return value.model_dump(mode='json')


def _row_dict(row) -> dict:
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


class SqlRepositories:
    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None:
        self.factory = factory

    async def current(self, identity_key: str) -> StateVersion | None:
        async with self.factory() as session:
            stmt = (
                select(db.StateVersionRow)
                .join(db.CurrentStateProjectionRow, db.CurrentStateProjectionRow.state_version_id == db.StateVersionRow.state_version_id)
                .where(db.CurrentStateProjectionRow.identity_key == identity_key)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return row_to_state(row) if row else None

    async def get_version(self, state_version_id: str) -> StateVersion | None:
        async with self.factory() as session:
            row = await session.get(db.StateVersionRow, state_version_id)
            return row_to_state(row) if row else None

    async def history(self, identity_key: str, *, limit: int = 50) -> list[StateVersion]:
        async with self.factory() as session:
            rows = (
                await session.execute(
                    select(db.StateVersionRow)
                    .where(db.StateVersionRow.identity_key == identity_key)
                    .order_by(db.StateVersionRow.version.desc())
                    .limit(limit)
                )
            ).scalars().all()
            return [row_to_state(row) for row in rows]

    async def list_current(self) -> list[StateVersion]:
        async with self.factory() as session:
            rows = (
                await session.execute(
                    select(db.StateVersionRow).join(
                        db.CurrentStateProjectionRow,
                        db.CurrentStateProjectionRow.state_version_id == db.StateVersionRow.state_version_id,
                    )
                )
            ).scalars().all()
            return [row_to_state(row) for row in rows]

    async def publish_state(
        self,
        state: StateVersion,
        *,
        events: list[DomainEvent],
        idempotency_scope: str | None = None,
        idempotency_key: str | None = None,
    ) -> StateVersion:
        async with self.factory() as session, session.begin():
            if idempotency_scope and idempotency_key:
                existing = await session.get(db.IdempotencyRow, (idempotency_scope, idempotency_key))
                if existing:
                    row = await session.get(db.StateVersionRow, existing.result_id)
                    if row:
                        return row_to_state(row)

            projection = await session.get(
                db.CurrentStateProjectionRow, state.identity.key, with_for_update=True
            )
            if projection:
                incumbent = await session.get(
                    db.StateVersionRow, projection.state_version_id, with_for_update=True
                )
                if incumbent:
                    incumbent.lifecycle_status = PublishedStateLifecycle.REPLACED.value
                    state.predecessor_state_version_id = incumbent.state_version_id
                    state.version = incumbent.version + 1
            else:
                state.version = 1

            session.add(state_to_row(state))
            await session.flush()
            if projection:
                projection.state_version_id = state.state_version_id
                projection.updated_at = state.created_at
            else:
                session.add(
                    db.CurrentStateProjectionRow(
                        identity_key=state.identity.key,
                        state_version_id=state.state_version_id,
                        updated_at=state.created_at,
                    )
                )
            for evidence_id in state.evidence_ids:
                session.add(
                    db.StateEvidenceLinkRow(
                        state_version_id=state.state_version_id,
                        evidence_id=evidence_id,
                    )
                )
            for event in events:
                await self._append_event_tx(session, event)
            if idempotency_scope and idempotency_key:
                session.add(
                    db.IdempotencyRow(
                        scope=idempotency_scope,
                        idempotency_key=idempotency_key,
                        result_id=state.state_version_id,
                        created_at=state.created_at,
                    )
                )
        return state

    async def expire_state(self, state_version_id: str, *, event: DomainEvent) -> StateVersion:
        async with self.factory() as session, session.begin():
            row = await session.get(db.StateVersionRow, state_version_id, with_for_update=True)
            if not row:
                raise NotFound('state version not found')
            if row.lifecycle_status == PublishedStateLifecycle.REPLACED.value:
                raise Conflict('replaced state cannot be expired as current')
            row.lifecycle_status = PublishedStateLifecycle.EXPIRED.value
            projection = await session.get(db.CurrentStateProjectionRow, row.identity_key, with_for_update=True)
            if projection and projection.state_version_id == state_version_id:
                await session.delete(projection)
            await self._append_event_tx(session, event)
            await session.flush()
            return row_to_state(row)

    async def save_observation(self, observation: ObservationRecord) -> ObservationRecord:
        async with self.factory() as session, session.begin():
            session.add(db.ObservationRow(**self._observation_data(observation)))
        return observation

    async def get_observation(self, observation_id: str) -> ObservationRecord | None:
        async with self.factory() as session:
            row = await session.get(db.ObservationRow, observation_id)
            return self._observation_model(row) if row else None

    async def update_observation(self, observation: ObservationRecord) -> ObservationRecord:
        async with self.factory() as session, session.begin():
            row = await session.get(db.ObservationRow, observation.observation_id, with_for_update=True)
            if not row:
                raise NotFound('observation not found')
            for key, value in self._observation_data(observation).items():
                setattr(row, key, value)
        return observation

    @staticmethod
    def _observation_data(observation: ObservationRecord) -> dict:
        data = observation.model_dump(mode='json')
        data['identity'] = observation.identity.model_dump(mode='json')
        data['proposed_value'] = observation.proposed_value.model_dump(mode='json')
        data['epistemic_status'] = observation.epistemic_status.value
        data['status'] = observation.status.value
        data['location_evidence_type'] = observation.location_evidence_type.value
        return data

    @staticmethod
    def _observation_model(row: db.ObservationRow) -> ObservationRecord:
        return ObservationRecord.model_validate({
            'observation_id': row.observation_id,
            'identity': row.identity,
            'proposed_value': row.proposed_value,
            'source_id': row.source_id,
            'actor_subject': row.actor_subject,
            'epistemic_status': row.epistemic_status,
            'status': row.status,
            'observed_at': row.observed_at,
            'received_at': row.received_at,
            'latitude': row.latitude,
            'longitude': row.longitude,
            'location_accuracy_m': row.location_accuracy_m,
            'location_description': row.location_description,
            'location_evidence_type': row.location_evidence_type,
            'evidence_ids': row.evidence_ids or [],
            'original_input_ref': row.original_input_ref,
            'interpretation_confidence': row.interpretation_confidence,
            'consumed_state_version_id': row.consumed_state_version_id,
            'correlation_id': row.correlation_id,
        })

    async def find_active_request(self, fingerprint: str) -> StateRequest | None:
        active = [x.value for x in (StateRequestStatus.REQUESTED, StateRequestStatus.ACQUIRING, StateRequestStatus.VERIFYING)]
        async with self.factory() as session:
            row = (
                await session.execute(
                    select(db.StateRequestRow)
                    .where(db.StateRequestRow.fingerprint == fingerprint, db.StateRequestRow.status.in_(active))
                    .order_by(db.StateRequestRow.created_at.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            return self._request_model(row) if row else None

    async def save_request(self, request: StateRequest) -> StateRequest:
        async with self.factory() as session, session.begin():
            row = await session.get(db.StateRequestRow, request.request_id, with_for_update=True)
            data = self._request_data(request)
            if row:
                for key, value in data.items(): setattr(row, key, value)
            else:
                session.add(db.StateRequestRow(**data))
        return request

    async def get_request(self, request_id: str) -> StateRequest | None:
        async with self.factory() as session:
            row = await session.get(db.StateRequestRow, request_id)
            return self._request_model(row) if row else None

    async def active_demand_count(self, identity_key: str) -> int:
        active = [x.value for x in (StateRequestStatus.REQUESTED, StateRequestStatus.ACQUIRING, StateRequestStatus.VERIFYING)]
        async with self.factory() as session:
            value = (
                await session.execute(
                    select(func.coalesce(func.sum(db.StateRequestRow.demand_count), 0)).where(
                        db.StateRequestRow.identity_key == identity_key,
                        db.StateRequestRow.status.in_(active),
                    )
                )
            ).scalar_one()
            return int(value)

    @staticmethod
    def _request_data(request: StateRequest) -> dict:
        data=request.model_dump()
        return {
            **data,
            'identity': request.identity.model_dump(mode='json'),
            'identity_key': request.identity.key,
            'decision_context': request.decision_context.model_dump(mode='json'),
            'gap_reason': request.gap_reason.value,
            'status': request.status.value,
        }

    @staticmethod
    def _request_model(row: db.StateRequestRow) -> StateRequest:
        return StateRequest.model_validate({
            'request_id': row.request_id, 'identity': row.identity,
            'requester_subject': row.requester_subject, 'decision_context': row.decision_context,
            'gap_reason': row.gap_reason, 'fingerprint': row.fingerprint, 'status': row.status,
            'demand_count': row.demand_count, 'created_at': row.created_at,
            'updated_at': row.updated_at, 'resolved_state_version_id': row.resolved_state_version_id,
        })

    async def save_job(self, job: AcquisitionJob) -> AcquisitionJob:
        async with self.factory() as session, session.begin():
            row = await session.get(db.AcquisitionJobRow, job.job_id, with_for_update=True)
            data={**job.model_dump(mode='json'), 'identity': job.identity.model_dump(mode='json'), 'decision_context': job.decision_context.model_dump(mode='json'), 'status': job.status.value}
            if row:
                for key,value in data.items(): setattr(row,key,value)
            else: session.add(db.AcquisitionJobRow(**data))
        return job

    async def get_job(self, job_id: str) -> AcquisitionJob | None:
        async with self.factory() as session:
            row=await session.get(db.AcquisitionJobRow, job_id)
            return AcquisitionJob.model_validate({**_row_dict(row), 'identity': row.identity, 'decision_context': row.decision_context, 'status': row.status}) if row else None

    async def pending_jobs(self, *, limit: int = 100) -> list[AcquisitionJob]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.AcquisitionJobRow).where(db.AcquisitionJobRow.status.in_([AcquisitionJobStatus.PENDING.value, AcquisitionJobStatus.IN_PROGRESS.value])).order_by(db.AcquisitionJobRow.created_at).limit(limit))).scalars().all()
            return [AcquisitionJob.model_validate({**_row_dict(r), 'identity':r.identity,'decision_context':r.decision_context,'status':r.status}) for r in rows]

    async def save_attempt(self, attempt: AcquisitionAttempt) -> AcquisitionAttempt:
        async with self.factory() as session, session.begin():
            row=await session.get(db.AcquisitionAttemptRow, attempt.attempt_id, with_for_update=True)
            data={**attempt.model_dump(mode='json'), 'status':attempt.status.value}
            if row:
                for k,v in data.items(): setattr(row,k,v)
            else: session.add(db.AcquisitionAttemptRow(**data))
        return attempt

    async def attempts_for_job(self, job_id: str) -> list[AcquisitionAttempt]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.AcquisitionAttemptRow).where(db.AcquisitionAttemptRow.job_id==job_id).order_by(db.AcquisitionAttemptRow.started_at))).scalars().all()
            return [AcquisitionAttempt.model_validate({**_row_dict(r),'status':r.status}) for r in rows]

    async def get_process_by_fingerprint(self, fingerprint: str) -> WatchProcess | None:
        async with self.factory() as session:
            row=(await session.execute(select(db.WatchProcessRow).where(db.WatchProcessRow.fingerprint==fingerprint))).scalar_one_or_none()
            return WatchProcess.model_validate({**_row_dict(row),'condition':row.condition}) if row else None

    async def get_process(self, watch_process_id: str) -> WatchProcess | None:
        async with self.factory() as session:
            row=await session.get(db.WatchProcessRow,watch_process_id); return WatchProcess.model_validate({**_row_dict(row),'condition':row.condition}) if row else None

    async def save_process(self, process: WatchProcess) -> WatchProcess:
        async with self.factory() as session, session.begin():
            existing=(await session.execute(select(db.WatchProcessRow).where(db.WatchProcessRow.fingerprint==process.fingerprint))).scalar_one_or_none()
            if not existing: session.add(db.WatchProcessRow(watch_process_id=process.watch_process_id,fingerprint=process.fingerprint,condition=process.condition.model_dump(mode='json'),created_at=process.created_at))
            else: process=WatchProcess.model_validate({**_row_dict(existing),'condition':existing.condition})
        return process

    async def save_subscription(self, subscription: WatchSubscription) -> WatchSubscription:
        async with self.factory() as session, session.begin():
            row=await session.get(db.WatchSubscriptionRow,subscription.watch_id,with_for_update=True)
            data={**subscription.model_dump(mode='json'),'status':subscription.status.value}
            if row:
                for k,v in data.items(): setattr(row,k,v)
            else: session.add(db.WatchSubscriptionRow(**data))
        return subscription

    async def get_subscription(self, watch_id: str) -> WatchSubscription | None:
        async with self.factory() as session:
            r=await session.get(db.WatchSubscriptionRow,watch_id); return WatchSubscription.model_validate({**_row_dict(r),'status':r.status}) if r else None

    async def list_subscriptions(self, subject: str) -> list[WatchSubscription]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.WatchSubscriptionRow).where(db.WatchSubscriptionRow.subscriber_subject==subject).order_by(db.WatchSubscriptionRow.created_at.desc()))).scalars().all(); return [WatchSubscription.model_validate({**_row_dict(r),'status':r.status}) for r in rows]

    async def subscriptions_for_identity(self, identity_key: str) -> list[WatchSubscription]:
        async with self.factory() as session:
            processes=(await session.execute(select(db.WatchProcessRow))).scalars().all()
            ids=[p.watch_process_id for p in processes if (p.condition or {}).get('identity',{}).get('entity_id') and __import__('pipe4.domain.state.identity',fromlist=['StateIdentity']).StateIdentity.model_validate(p.condition['identity']).key==identity_key]
            if not ids: return []
            rows=(await session.execute(select(db.WatchSubscriptionRow).where(db.WatchSubscriptionRow.watch_process_id.in_(ids)))).scalars().all(); return [WatchSubscription.model_validate({**_row_dict(r),'status':r.status}) for r in rows]

    async def delete_subscription(self, watch_id: str) -> None:
        async with self.factory() as session, session.begin(): await session.execute(delete(db.WatchSubscriptionRow).where(db.WatchSubscriptionRow.watch_id==watch_id))

    async def active_watch_count(self, identity_key: str) -> int:
        return sum(1 for s in await self.subscriptions_for_identity(identity_key) if s.status != WatchStatus.PAUSED)

    async def save_access_request(self, request: AccessRequest) -> AccessRequest:
        async with self.factory() as session, session.begin():
            row=await session.get(db.AccessRequestRow,request.access_request_id,with_for_update=True); data={**request.model_dump(mode='json'),'status':request.status.value}
            if row:
                for k,v in data.items(): setattr(row,k,v)
            else: session.add(db.AccessRequestRow(**data))
        return request

    async def get_access_request(self, request_id: str) -> AccessRequest | None:
        async with self.factory() as session:
            r=await session.get(db.AccessRequestRow,request_id); return AccessRequest.model_validate({**_row_dict(r),'status':r.status}) if r else None

    async def list_access_requests(self, subject: str) -> list[AccessRequest]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.AccessRequestRow).where(db.AccessRequestRow.requester_subject==subject).order_by(db.AccessRequestRow.requested_at.desc()))).scalars().all(); return [AccessRequest.model_validate({**_row_dict(r),'status':r.status}) for r in rows]

    async def save_grant(self, grant: PermissionGrant) -> PermissionGrant:
        async with self.factory() as session, session.begin(): session.add(db.PermissionGrantRow(**grant.model_dump(mode='json')))
        return grant

    async def has_grant(self, *, subject: str, entity_id: str, identity_key: str | None, permission: str) -> bool:
        now=datetime.now(timezone.utc)
        async with self.factory() as session:
            stmt=select(func.count()).select_from(db.PermissionGrantRow).where(db.PermissionGrantRow.subject==subject,db.PermissionGrantRow.target_entity_id==entity_id,db.PermissionGrantRow.permission==permission,db.PermissionGrantRow.revoked_at.is_(None),(db.PermissionGrantRow.expires_at.is_(None)|(db.PermissionGrantRow.expires_at>now)),(db.PermissionGrantRow.target_identity_key.is_(None)|(db.PermissionGrantRow.target_identity_key==identity_key)))
            return int((await session.execute(stmt)).scalar_one())>0

    async def revoke_grant(self, access_request_id: str, *, revoked_at: datetime) -> None:
        async with self.factory() as session, session.begin(): await session.execute(update(db.PermissionGrantRow).where(db.PermissionGrantRow.access_request_id==access_request_id,db.PermissionGrantRow.revoked_at.is_(None)).values(revoked_at=revoked_at))

    async def pending_request_status(self, *, subject: str, entity_id: str, identity_key: str | None) -> str | None:
        async with self.factory() as session:
            stmt=select(db.AccessRequestRow.status).where(db.AccessRequestRow.requester_subject==subject,db.AccessRequestRow.target_entity_id==entity_id,db.AccessRequestRow.status==AccessRequestStatus.PENDING.value,(db.AccessRequestRow.target_identity_key.is_(None)|(db.AccessRequestRow.target_identity_key==identity_key))).order_by(db.AccessRequestRow.requested_at.desc()).limit(1); return (await session.execute(stmt)).scalar_one_or_none()

    async def save_entity(self, entity: ReferenceEntity) -> ReferenceEntity:
        async with self.factory() as session, session.begin():
            geom=None
            if entity.latitude is not None and entity.longitude is not None: geom=f'SRID=4326;POINT({entity.longitude} {entity.latitude})'
            row=await session.get(db.ReferenceEntityRow,entity.entity_id,with_for_update=True)
            data={**entity.model_dump(mode='json'),'geom':geom}
            if row:
                for k,v in data.items(): setattr(row,k,v)
            else: session.add(db.ReferenceEntityRow(**data))
        return entity

    async def get_entity(self, entity_id: str) -> ReferenceEntity | None:
        async with self.factory() as session:
            r=await session.get(db.ReferenceEntityRow,entity_id); return ReferenceEntity.model_validate({k:v for k,v in _row_dict(r).items() if k!='geom'}) if r else None

    async def list_entities(self) -> list[ReferenceEntity]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.ReferenceEntityRow))).scalars().all(); return [ReferenceEntity.model_validate({k:v for k,v in _row_dict(r).items() if k!='geom'}) for r in rows]

    async def save_targeted(self, request: TargetedAcquisitionRequest) -> TargetedAcquisitionRequest:
        async with self.factory() as session, session.begin():
            row=await session.get(db.TargetedAcquisitionRow,request.targeted_request_id,with_for_update=True); data={**request.model_dump(mode='json'),'status':request.status.value}
            if row:
                for k,v in data.items(): setattr(row,k,v)
            else: session.add(db.TargetedAcquisitionRow(**data))
        return request

    async def get_targeted(self, request_id: str) -> TargetedAcquisitionRequest | None:
        async with self.factory() as session:
            r=await session.get(db.TargetedAcquisitionRow,request_id); return TargetedAcquisitionRequest.model_validate({**_row_dict(r),'status':r.status}) if r else None

    async def list_targeted_for_subject(self, subject: str) -> list[TargetedAcquisitionRequest]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.TargetedAcquisitionRow).where(db.TargetedAcquisitionRow.target_subject==subject).order_by(db.TargetedAcquisitionRow.offered_at.desc()))).scalars().all(); return [TargetedAcquisitionRequest.model_validate({**_row_dict(r),'status':r.status}) for r in rows]

    async def save_contradiction(self, contradiction: ContradictionRecord) -> ContradictionRecord:
        async with self.factory() as session, session.begin(): session.add(db.ContradictionRow(**{**contradiction.model_dump(mode='json'),'status':contradiction.status.value}))
        return contradiction

    async def open_for_identity(self, identity_key: str) -> list[ContradictionRecord]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.ContradictionRow).where(db.ContradictionRow.identity_key==identity_key,db.ContradictionRow.status==ContradictionStatus.OPEN.value))).scalars().all(); return [ContradictionRecord.model_validate({**_row_dict(r),'status':r.status}) for r in rows]

    async def append_event(self, event: DomainEvent) -> None:
        async with self.factory() as session, session.begin(): await self._append_event_tx(session,event)

    async def append_events(self, events: list[DomainEvent]) -> None:
        async with self.factory() as session, session.begin():
            for event in events: await self._append_event_tx(session,event)

    @staticmethod
    async def _append_event_tx(session: AsyncSession, event: DomainEvent) -> None:
        session.add(db.DomainEventRow(event_id=event.event_id,event_type=event.event_type,aggregate_type=event.aggregate_type,aggregate_id=event.aggregate_id,occurred_at=event.occurred_at,correlation_id=event.correlation_id,payload=event.payload))
        out=OutboxRecord(event=event,created_at=event.occurred_at)
        session.add(db.OutboxRow(outbox_id=out.outbox_id,event_id=event.event_id,event_payload=event.model_dump(mode='json'),created_at=out.created_at,attempts=0))

    async def list_events(self, *, limit: int = 200) -> list[DomainEvent]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.DomainEventRow).order_by(db.DomainEventRow.occurred_at.desc()).limit(limit))).scalars().all(); return [DomainEvent.model_validate(_row_dict(r)) for r in reversed(rows)]

    async def pending_outbox(self, *, limit: int = 100) -> list[OutboxRecord]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.OutboxRow).where(db.OutboxRow.published_at.is_(None)).order_by(db.OutboxRow.created_at).limit(limit))).scalars().all()
            return [OutboxRecord(outbox_id=r.outbox_id,event=DomainEvent.model_validate(r.event_payload),created_at=r.created_at,published_at=r.published_at,attempts=r.attempts,last_error=r.last_error) for r in rows]

    async def mark_outbox_published(self, outbox_id: str, *, published_at: datetime) -> None:
        async with self.factory() as session, session.begin(): await session.execute(update(db.OutboxRow).where(db.OutboxRow.outbox_id==outbox_id).values(published_at=published_at))

    async def mark_outbox_failed(self, outbox_id: str, *, error: str) -> None:
        async with self.factory() as session, session.begin(): await session.execute(update(db.OutboxRow).where(db.OutboxRow.outbox_id==outbox_id).values(attempts=db.OutboxRow.attempts+1,last_error=error[:2000]))
