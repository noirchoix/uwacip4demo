from __future__ import annotations

from datetime import timedelta

from pipe4.application.common import event
from pipe4.domain.events.models import DomainEvent
from pipe4.domain.state.enums import EpistemicStatus, PublishedStateLifecycle, VerificationStatus, VisibilityScope
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.models import ConfidenceBreakdown, StateVersion
from pipe4.domain.state.values import StateValue
from pipe4.ports.clock import Clock
from pipe4.ports.jobs import JobSchedulerPort
from pipe4.repositories.protocols import StatePublicationPort
from pipe4.domain.policies.registry import PolicyRegistry


class PublicationService:
    def __init__(self, *, repository: StatePublicationPort, policies: PolicyRegistry, clock: Clock, jobs: JobSchedulerPort | None = None) -> None:
        self.repository=repository; self.policies=policies; self.clock=clock; self.jobs=jobs

    async def publish(
        self,
        *,
        identity: StateIdentity,
        value: StateValue,
        epistemic_status: EpistemicStatus,
        verification_status: VerificationStatus,
        observed_at,
        received_at,
        confidence: ConfidenceBreakdown,
        source_ids: list[str],
        evidence_ids: list[str],
        visibility: VisibilityScope=VisibilityScope.PUBLIC,
        permission_tags: set[str] | None=None,
        lifecycle_status: PublishedStateLifecycle=PublishedStateLifecycle.CURRENT,
        last_verified_at=None,
        idempotency_scope: str | None=None,
        idempotency_key: str | None=None,
        correlation_id: str | None=None,
    ) -> StateVersion:
        now=self.clock.now(); state_policy=self.policies.state_type(identity.state_type); freshness=state_policy.freshness
        if value.kind not in state_policy.allowed_value_kinds:
            raise ValueError(f'value kind {value.kind!r} is not allowed for {identity.state_type.value}')
        state=StateVersion(
            identity=identity,value=value,epistemic_status=epistemic_status,verification_status=verification_status,lifecycle_status=lifecycle_status,
            observed_at=observed_at,received_at=received_at,valid_from=observed_at,expires_at=observed_at+timedelta(seconds=freshness.fresh_seconds),last_verified_at=last_verified_at,
            confidence=confidence.weighted_score,confidence_breakdown=confidence,policy_version=self.policies.bundle.version,
            visibility=visibility,permission_tags=permission_tags or set(),source_ids=list(dict.fromkeys(source_ids)),evidence_ids=list(dict.fromkeys(evidence_ids)),correlation_id=correlation_id,created_at=now,
        )
        evt=event('state.published',aggregate_type='state_version',aggregate_id=state.state_version_id,occurred_at=now,correlation_id=correlation_id,payload={'identity_key':identity.key,'entity_id':identity.entity_id,'state_type':identity.state_type.value,'lifecycle_status':lifecycle_status.value})
        result=await self.repository.publish_state(state,events=[evt],idempotency_scope=idempotency_scope,idempotency_key=idempotency_key)
        if self.jobs:
            await self.jobs.enqueue_watch_evaluation(result.state_version_id)
            await self.jobs.enqueue_outbox_dispatch()
        return result

    async def expire(self, state_version_id: str, *, correlation_id: str | None=None) -> StateVersion:
        now=self.clock.now(); evt=event('state.expired',aggregate_type='state_version',aggregate_id=state_version_id,occurred_at=now,correlation_id=correlation_id)
        state=await self.repository.expire_state(state_version_id,event=evt)
        if self.jobs: await self.jobs.enqueue_outbox_dispatch()
        return state
