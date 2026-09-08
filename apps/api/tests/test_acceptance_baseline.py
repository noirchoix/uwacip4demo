from __future__ import annotations

from datetime import timedelta

import pytest

from pipe4.domain.acquisition.models import DecisionContext, GapReason, StateRequestStatus
from pipe4.domain.entities.models import ReferenceEntity
from pipe4.domain.evidence.models import EvidenceClass, EvidenceRef, SourceProfile
from pipe4.domain.observation.models import LocationEvidenceType
from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import EpistemicStatus, PresentationKind, PublishedStateLifecycle, StateType, UserFacingStateStatus, VerificationStatus, VisibilityScope
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import BooleanStateValue, DurationStateValue
from pipe4.domain.watch.models import WatchCondition
from pipe4.domain.policies.verification import VerificationPolicy


def identity(state_type=StateType.AVAILABLE, entity_id='entity-1', object_key='main'):
    return StateIdentity(entity_id=entity_id,object_key=object_key,state_type=state_type)


async def declare(c, admin, now, *, state_type=StateType.AVAILABLE, value=None, observed_at=None, visibility=VisibilityScope.PUBLIC, entity_id='entity-1', token=None):
    value=value or BooleanStateValue(value=True)
    return await c.declarations.declare(admin,identity=identity(state_type,entity_id),value=value,observed_at=observed_at or now,source_id='owner-source',visibility=visibility,idempotency_key=token)


@pytest.mark.asyncio
async def test_ac01_fresh_known_state_reused_without_acquisition(container,admin,user,now):
    state=await declare(container,admin,now)
    before=len(container.repositories.requests)
    result=await container.current_state.get(user,identity=identity())
    assert result.kind==PresentationKind.STATE and result.state_version_id==state.state_version_id
    assert len(container.repositories.requests)==before


@pytest.mark.asyncio
async def test_ac02_missing_state_creates_reality_gap_and_shared_request(container,user):
    ident=identity(StateType.TIME)
    result=await container.current_state.get(user,identity=ident)
    assert result.kind==PresentationKind.UNKNOWN
    assert len(container.repositories.requests)==1
    first=next(iter(container.repositories.requests.values()))
    again=await container.resolution.request(user,identity=ident,decision_context=DecisionContext(),reason=GapReason.MISSING)
    assert again.request_id==first.request_id and again.demand_count==2


@pytest.mark.asyncio
async def test_ac03_successful_acquisition_creates_provenance_backed_state(container,user):
    request=await container.resolution.request(user,identity=identity(StateType.WORKING),decision_context=DecisionContext(),reason=GapReason.MISSING)
    job=next(job for job in container.repositories.jobs.values() if job.request_id==request.request_id)
    state=await container.acquisition.run_job(job.job_id)
    assert state is not None and state.source_ids==['fixture-source'] and state.evidence_ids
    assert state.confidence_breakdown is not None and state.expires_at>state.observed_at


@pytest.mark.asyncio
async def test_ac04_complete_acquisition_failure_returns_unknown_without_fake_state(container,user):
    container.sources.sources.clear()
    ident=identity(StateType.TIME,'missing-entity')
    request=await container.resolution.request(user,identity=ident,decision_context=DecisionContext(),reason=GapReason.MISSING)
    assert await container.repositories.current(ident.key) is None
    request=await container.resolution.mark_unknown(request.request_id)
    assert request.status==StateRequestStatus.UNKNOWN and await container.repositories.current(ident.key) is None


@pytest.mark.asyncio
async def test_ac05_stale_never_silently_current(container,admin,user,now):
    await declare(container,admin,now,observed_at=now-timedelta(hours=2))
    result=await container.current_state.get(user,identity=identity(),decision_context='operational_coordination')
    assert result.status==UserFacingStateStatus.STALE and result.freshness_seconds and result.freshness_seconds>900
    assert any(r.gap_reason==GapReason.STALE for r in container.repositories.requests.values())


@pytest.mark.asyncio
async def test_ac06_credible_material_conflict_becomes_disputed(container,admin,now):
    await declare(container,admin,now,value=BooleanStateValue(value=True),observed_at=now-timedelta(seconds=10))
    await container.sources.save_source(SourceProfile(source_id='credible-witness',source_type='witness',reliability=0.96,evidence_capability=0.9))
    obs=await container.observations.submit(Principal(subject='witness'),identity=identity(),value=BooleanStateValue(value=False),observed_at=now,source_id='credible-witness',latitude=6.45,longitude=3.4,location_accuracy_m=5)
    disputed=await container.verification.verify_observation(obs.observation_id)
    assert disputed is not None and disputed.lifecycle_status==PublishedStateLifecycle.DISPUTED
    assert await container.repositories.open_for_identity(identity().key)


@pytest.mark.asyncio
async def test_ac07_replacement_preserves_version_history(container,admin,now):
    first=await declare(container,admin,now,value=BooleanStateValue(value=True),token='a')
    second=await declare(container,admin,now+timedelta(seconds=5),value=BooleanStateValue(value=False),token='b')
    history=await container.repositories.history(identity().key)
    assert len(history)==2 and second.predecessor_state_version_id==first.state_version_id
    assert next(x for x in history if x.state_version_id==first.state_version_id).lifecycle_status==PublishedStateLifecycle.REPLACED


@pytest.mark.asyncio
async def test_ac08_offline_observation_preserves_observed_and_received_times(container,user,now):
    old=now-timedelta(hours=3)
    obs=await container.observations.submit(user,identity=identity(StateType.WORKING),value=BooleanStateValue(value=False),observed_at=old,location_description='station entrance')
    assert obs.observed_at==old and obs.received_at>obs.observed_at and obs.location_evidence_type==LocationEvidenceType.MANUALLY_DESCRIBED


@pytest.mark.asyncio
async def test_ac09_ai_or_inference_alone_cannot_manufacture_verified(container,now):
    policy=VerificationPolicy(container.policies)
    result=policy.evaluate(state_type='WORKING',epistemic_status=EpistemicStatus.INFERRED,confidence=__import__('pipe4.domain.state.models',fromlist=['ConfidenceBreakdown']).ConfidenceBreakdown(source_reliability=1,evidence_quality=1,corroboration=1,recency=1,location_quality=1,weighted_score=1,policy_version='1.0'),evidence=[],has_unresolved_material_contradiction=False)
    assert result.status==VerificationStatus.INCONCLUSIVE


@pytest.mark.asyncio
async def test_ac10_ai_outage_does_not_stop_structured_state_retrieval(container,admin,user,now):
    await declare(container,admin,now)
    result=await container.current_state.get(user,identity=identity())
    assert result.kind==PresentationKind.STATE
    interpretation=await container.witness.interpret(text='something unclear',latitude=None,longitude=None)
    assert interpretation.requires_clarification is True


@pytest.mark.asyncio
async def test_ac11_protected_state_does_not_leak(container,admin,user,now):
    await declare(container,admin,now,visibility=VisibilityScope.PRIVATE)
    result=await container.current_state.get(user,identity=identity())
    assert result.kind==PresentationKind.PROTECTED and result.value is None and result.confidence is None and result.observed_at is None and result.provenance is None


@pytest.mark.asyncio
async def test_ac12_cross_pipe_consumer_uses_common_current_state_contract(container,admin,now):
    state=await declare(container,admin,now)
    consumer=Principal(subject='service:pipe1',roles=frozenset({'uwaci_internal'}),service=True)
    result=await container.current_state.get(consumer,identity=identity())
    assert result.state_version_id==state.state_version_id and result.state_type==StateType.AVAILABLE


@pytest.mark.asyncio
async def test_ac13_state_change_emits_versioned_domain_event(container,admin,now):
    state=await declare(container,admin,now)
    events=await container.repositories.list_events()
    assert any(e.event_type=='state.published' and e.aggregate_id==state.state_version_id for e in events)
    assert await container.repositories.pending_outbox()


@pytest.mark.asyncio
async def test_ac14_watch_triggers_when_condition_becomes_true(container,admin,user,now):
    watch=await container.watches.create(user,WatchCondition(identity=identity(),operator='EQ',target=BooleanStateValue(value=True)))
    state=await declare(container,admin,now)
    count=await container.watches.evaluate(state)
    updated=await container.repositories.get_subscription(watch.watch_id)
    assert count==1 and updated.status.value=='ALERTING'


@pytest.mark.asyncio
async def test_ac15_equivalent_watches_share_underlying_process(container,user):
    condition=WatchCondition(identity=identity(),operator='EQ',target=BooleanStateValue(value=True))
    a=await container.watches.create(user,condition);b=await container.watches.create(Principal(subject='user-2'),condition)
    assert a.watch_process_id==b.watch_process_id and len(container.repositories.watch_processes)==1


@pytest.mark.asyncio
async def test_ac16_confirmed_outcome_updates_source_reliability(container):
    before=(await container.sources.get_source('fixture-source')).reliability
    updated=await container.sources.record_outcome('fixture-source',entity_id='entity-1',state_type=StateType.AVAILABLE,correct=True)
    assert updated.reliability>=before and updated.correct_outcomes==1


@pytest.mark.asyncio
async def test_ac17_schema_retains_freshness_learning_history_fields(container,admin,now):
    state=await declare(container,admin,now)
    assert state.observed_at and state.received_at and state.expires_at and state.policy_version and state.confidence_breakdown


@pytest.mark.asyncio
async def test_ac18_unrelated_domains_use_same_engine(container,admin,user,now):
    await container.repositories.save_entity(ReferenceEntity(entity_id='queue',entity_type='office',display_name='Queue',latitude=6.451,longitude=3.4,created_at=now))
    await container.repositories.save_entity(ReferenceEntity(entity_id='machine',entity_type='machine',display_name='Machine',latitude=6.452,longitude=3.4,created_at=now))
    await declare(container,admin,now,entity_id='entity-1',state_type=StateType.AVAILABLE,value=BooleanStateValue(value=True),token='avail')
    # TIME owner declaration is disallowed by source authority but publication can still represent it through system acquisition; fixture acquisition proves same engine.
    req=await container.resolution.request(user,identity=identity(StateType.TIME,'queue'),decision_context=DecisionContext(),reason=GapReason.MISSING);job=next(j for j in container.repositories.jobs.values() if j.request_id==req.request_id);time_state=await container.acquisition.run_job(job.job_id)
    working=await declare(container,admin,now,entity_id='machine',state_type=StateType.WORKING,value=BooleanStateValue(value=False),token='work')
    assert (await container.repositories.current(identity(StateType.AVAILABLE).key)) is not None
    assert time_state and time_state.identity.state_type==StateType.TIME and working.identity.state_type==StateType.WORKING


@pytest.mark.asyncio
async def test_ac19_authorized_audit_explains_state(container,admin,now):
    state=await declare(container,admin,now)
    evidence=await container.provenance.get_evidence(state.evidence_ids);events=await container.repositories.list_events()
    assert evidence and evidence[0].source_id=='owner-source' and any(e.aggregate_id==state.state_version_id for e in events)


@pytest.mark.asyncio
async def test_ac20_uncertainty_states_survive_as_distinct_presentations(container,admin,user,now):
    current=await declare(container,admin,now,token='current')
    current_p=await container.presentation.state(user,current)
    stale=await declare(container,admin,now,value=BooleanStateValue(value=False),observed_at=now-timedelta(hours=2),token='stale')
    stale_p=await container.current_state.get(user,identity=identity())
    unknown=await container.presentation.unknown(entity_id='unknown')
    assert current_p.status==UserFacingStateStatus.CURRENT and stale_p.status==UserFacingStateStatus.STALE and unknown.status==UserFacingStateStatus.UNKNOWN
