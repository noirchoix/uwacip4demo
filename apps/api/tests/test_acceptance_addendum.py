from __future__ import annotations

from datetime import timedelta

import pytest

from pipe4.domain.entities.models import ReferenceEntity
from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import PresentationKind, StateType, UserFacingStateStatus, VisibilityScope
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import BooleanStateValue, DurationStateValue
from pipe4.domain.watch.models import WatchCondition

async def declare(c,admin,now,identity,value,visibility=VisibilityScope.PUBLIC,token=None): return await c.declarations.declare(admin,identity=identity,value=value,observed_at=now,source_id='owner-source',visibility=visibility,idempotency_key=token)

@pytest.mark.asyncio
async def test_add_ac01_access_pending_approved_without_leakage(container,admin,user,now):
    ident=StateIdentity(entity_id='entity-1',state_type=StateType.AVAILABLE);await declare(container,admin,now,ident,BooleanStateValue(value=True),VisibilityScope.PRIVATE,'p')
    before=await container.current_state.get(user,identity=ident);assert before.kind==PresentationKind.PROTECTED and before.value is None
    req=await container.access.request(user,entity_id='entity-1',identity_key=ident.key);pending=await container.current_state.get(user,identity=ident);assert pending.access_request_status=='PENDING'
    await container.access.decide(admin,req.access_request_id,approve=True);after=await container.current_state.get(user,identity=ident);assert after.kind==PresentationKind.STATE and after.value.value is True

@pytest.mark.asyncio
async def test_add_ac02_nearby_mixed_domain_ranking(container,admin,user,now):
    items=[('entity-1',StateType.AVAILABLE,BooleanStateValue(value=True),6.45),('clinic',StateType.WORKING,BooleanStateValue(value=False),6.451),('queue',StateType.TIME,DurationStateValue(seconds=600),6.452)]
    for eid,stype,value,lat in items:
        if eid!='entity-1': await container.repositories.save_entity(ReferenceEntity(entity_id=eid,entity_type='service',display_name=eid,latitude=lat,longitude=3.4,created_at=now))
        if stype==StateType.TIME:
            # publish through fixture acquisition to respect source policy
            from pipe4.domain.acquisition.models import DecisionContext,GapReason
            req=await container.resolution.request(user,identity=StateIdentity(entity_id=eid,state_type=stype),decision_context=DecisionContext(),reason=GapReason.MISSING);job=next(j for j in container.repositories.jobs.values() if j.request_id==req.request_id);await container.acquisition.run_job(job.job_id)
        else: await declare(container,admin,now,StateIdentity(entity_id=eid,state_type=stype),value,token=eid)
    rows=await container.nearby.search(user,latitude=6.45,longitude=3.4,radius_m=5000)
    assert {r.current.state_type for r in rows}>={StateType.AVAILABLE,StateType.WORKING,StateType.TIME};assert rows==sorted(rows,key=lambda r:r.score,reverse=True)

@pytest.mark.asyncio
async def test_add_ac03_all_watches_manage(container,user):
    condition=WatchCondition(identity=StateIdentity(entity_id='entity-1',state_type=StateType.AVAILABLE),operator='EQ',target=BooleanStateValue(value=True));w=await container.watches.create(user,condition);views=await container.watches.list_views(user);assert views[0].watch_id==w.watch_id and views[0].condition.identity.key==condition.identity.key;assert (await container.watches.set_paused(user,w.watch_id,paused=True)).status.value=='PAUSED';assert (await container.watches.set_paused(user,w.watch_id,paused=False)).status.value=='ACTIVE';await container.watches.remove(user,w.watch_id);assert await container.watches.list(user)==[]

@pytest.mark.asyncio
async def test_add_ac04_public_witness_is_pseudonymized(container,user,now):
    obs=await container.observations.submit(user,identity=StateIdentity(entity_id='entity-1',state_type=StateType.WORKING),value=BooleanStateValue(value=False),observed_at=now)
    labels=await container.provenance.public_source_labels(source_ids=[obs.source_id],context_key=obs.identity.key)
    assert labels[0].startswith('Witness ') and user.subject not in labels[0]

@pytest.mark.asyncio
async def test_add_ac05_natural_language_report_infers_domain_and_location(container,user,now):
    result,obs=await container.witness.report(user,text='The station service is not working',observed_at=now,entity_id='entity-1',latitude=6.45,longitude=3.4,location_accuracy_m=8)
    assert obs is not None and obs.identity.state_type==StateType.WORKING and obs.proposed_value.value is False

@pytest.mark.asyncio
async def test_add_ac06_location_failure_manual_fallback_submits(container,user,now):
    result,obs=await container.witness.report(user,text='The station service is not working',observed_at=now,entity_id='entity-1',location_description='Beside the main station gate')
    assert obs is not None and obs.location_evidence_type.value=='MANUALLY_DESCRIBED'

@pytest.mark.asyncio
async def test_add_ac07_none_of_these_creates_provisional_without_overwrite(container,now):
    original=await container.entities.get('entity-1');provisional=await container.entity_resolution.provisional(entity_type='atm',display_name='ATM beside station',latitude=6.45,longitude=3.4);assert provisional.provisional is True and provisional.entity_id!='entity-1' and (await container.entities.get('entity-1')).display_name==original.display_name

@pytest.mark.asyncio
async def test_add_ac08_receipt_separates_you_reported_from_uwaci_verifying(container,user,now):
    text='The station service is not working';_,obs=await container.witness.report(user,text=text,observed_at=now,entity_id='entity-1');assert obs is not None and obs.status.value=='VERIFYING';current=await container.presentation.unknown(entity_id='entity-1',message='Uwaci is verifying a new report.');assert current.status==UserFacingStateStatus.UNKNOWN

@pytest.mark.asyncio
async def test_add_ac09_targeted_accept_reuses_normal_witness_flow(container,user,now):
    offer=await container.targeted.offer(state_request_id='gap-1',target_subject=user.subject);accepted=await container.targeted.respond(user,offer.targeted_request_id,accept=True);assert accepted.status.value=='ACCEPTED';_,obs=await container.witness.report(user,text='The station service is not working',observed_at=now,entity_id='entity-1');assert obs is not None;completed=await container.targeted.complete(user,offer.targeted_request_id,observation_id=obs.observation_id);assert completed.status.value=='COMPLETED' and completed.completed_observation_id==obs.observation_id

@pytest.mark.asyncio
async def test_add_ac10_one_presentation_contract_handles_unrelated_domains(container,admin,user,now):
    values=[(StateType.AVAILABLE,BooleanStateValue(value=True)),(StateType.WORKING,BooleanStateValue(value=False))]
    presentations=[]
    for i,(stype,value) in enumerate(values):
        state=await declare(container,admin,now,StateIdentity(entity_id='entity-1',object_key=f'o{i}',state_type=stype),value,token=f'x{i}');presentations.append(await container.presentation.state(user,state))
    assert all(type(p) is type(presentations[0]) for p in presentations) and {p.state_type for p in presentations}=={StateType.AVAILABLE,StateType.WORKING}
