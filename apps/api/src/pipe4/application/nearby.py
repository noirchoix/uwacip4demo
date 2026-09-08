from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pipe4.domain.principal import Principal
from pipe4.domain.policies.nearby import NearbyFactors, NearbyRankingEngine, distance_m
from pipe4.domain.state.models import CurrentStatePresentation
from pipe4.ports.authorization import AuthorizationPort
from pipe4.ports.clock import Clock
from pipe4.ports.entities import EntityCatalogPort
from pipe4.repositories.protocols import RequestRepository, StateRepository, WatchRepository

from .presentation import PresentationService


class NearbyResult(BaseModel):
    model_config=ConfigDict(extra='forbid')
    score: float=Field(ge=0,le=1)
    distance_m: float
    current: CurrentStatePresentation


class NearbyService:
    def __init__(self, *, states: StateRepository, entities: EntityCatalogPort, authorization: AuthorizationPort, presentation: PresentationService, ranking: NearbyRankingEngine, requests: RequestRepository, watches: WatchRepository, clock: Clock) -> None:
        self.states=states;self.entities=entities;self.authorization=authorization;self.presentation=presentation;self.ranking=ranking;self.requests=requests;self.watches=watches;self.clock=clock

    async def search(self, principal: Principal, *, latitude: float, longitude: float, radius_m: int, urgency: float=0.5, uncertainty_consequence: float=0.25, intent_relevance: float=0.5) -> list[NearbyResult]:
        rows=[];now=self.clock.now()
        for state in await self.states.list_current():
            entity=await self.entities.get(state.identity.entity_id)
            if not entity or entity.latitude is None or entity.longitude is None: continue
            dist=distance_m(latitude,longitude,entity.latitude,entity.longitude)
            if dist>radius_m: continue
            if not await self.authorization.can_view(principal,identity=state.identity,visibility=state.visibility,permission_tags=state.permission_tags): continue
            age=max(0,(now-state.observed_at).total_seconds());freshness=max(0.0,1-age/max((state.expires_at-state.observed_at).total_seconds() if state.expires_at else 900,1));proximity=max(0.0,1-dist/max(radius_m,1));demand=await self.requests.active_demand_count(state.identity.key);watch_count=await self.watches.active_watch_count(state.identity.key)
            score=self.ranking.score(NearbyFactors(proximity=proximity,intent_relevance=intent_relevance,urgency=urgency,uncertainty_consequence=uncertainty_consequence,freshness=freshness,confidence=state.confidence,recent_change=1.0 if state.identity.state_type.value=='CHANGED' else 0.0,active_demand=min(1.0,demand/5),watch_relevance=min(1.0,watch_count/5)))
            current=await self.presentation.state(principal,state,freshness_seconds=int(age),distance_m=dist);rows.append(NearbyResult(score=score,distance_m=dist,current=current))
        return sorted(rows,key=lambda x:x.score,reverse=True)
