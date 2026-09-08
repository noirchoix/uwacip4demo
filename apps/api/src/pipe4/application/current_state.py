from __future__ import annotations

from pipe4.domain.acquisition.models import DecisionContext, GapReason
from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import PublishedStateLifecycle, UserFacingStateStatus
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.models import CurrentStatePresentation, StateHistoryEntry
from pipe4.domain.policies.decision import DecisionEngine
from pipe4.domain.policies.freshness import FreshnessEngine
from pipe4.ports.clock import Clock
from pipe4.repositories.protocols import StateRepository

from .presentation import PresentationService


class CurrentStateService:
    def __init__(self, *, states: StateRepository, freshness: FreshnessEngine, decision: DecisionEngine, presentation: PresentationService, clock: Clock, resolution=None) -> None:
        self.states=states; self.freshness=freshness; self.decision=decision; self.presentation=presentation; self.clock=clock; self.resolution=resolution

    async def get(self, principal: Principal, *, identity: StateIdentity, decision_context: str='consumer_discovery', request_if_missing: bool=True) -> CurrentStatePresentation:
        state=await self.states.current(identity.key)
        if not state:
            if request_if_missing and self.resolution: await self.resolution.request(principal,identity=identity,decision_context=DecisionContext(name=decision_context),reason=GapReason.MISSING)
            return await self.presentation.unknown(entity_id=identity.entity_id,identity=identity)
        now=self.clock.now(); fresh=self.freshness.assess(state,now=now); assessment=self.decision.assess(state=state,freshness=fresh,decision_context=decision_context)
        if fresh.fresh:
            return await self.presentation.state(principal,state,freshness_seconds=fresh.age_seconds)
        if assessment.acceptable and assessment.allow_stale:
            return await self.presentation.state(principal,state,freshness_seconds=fresh.age_seconds,status_override=UserFacingStateStatus.STALE)
        if request_if_missing and self.resolution:
            await self.resolution.request(principal,identity=identity,decision_context=DecisionContext(name=decision_context),reason=GapReason.STALE)
        # Stale state remains visible only when authorized, clearly marked; strict consumers must revalidate.
        return await self.presentation.state(principal,state,freshness_seconds=fresh.age_seconds,status_override=UserFacingStateStatus.STALE)

    async def history(self, principal: Principal, *, identity: StateIdentity, limit: int=50) -> list[StateHistoryEntry]:
        rows=await self.states.history(identity.key,limit=limit); safe=[]
        for row in rows:
            presentation=await self.presentation.state(principal,row)
            if presentation.kind.value!='STATE': continue
            safe.append(StateHistoryEntry(state_version_id=row.state_version_id,status=row.lifecycle_status,state_type=row.identity.state_type,value=row.value,observed_at=row.observed_at,created_at=row.created_at,epistemic_status=row.epistemic_status,verification_status=row.verification_status,confidence=row.confidence))
        return safe
