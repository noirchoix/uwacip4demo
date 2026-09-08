from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pipe4.adapters.ai.deterministic import DeterministicInterpreter
from pipe4.domain.entities.models import EntityCandidate, EntityResolutionStatus
from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import StateType
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import StateValue
from pipe4.ports.ai import AIInterpretationPort
from pipe4.ports.evidence_store import EvidenceStorePort
from pipe4.exceptions import ExternalDependencyUnavailable

from .entities import EntityResolutionService
from .observations import ObservationService


class WitnessInterpretationResult(BaseModel):
    model_config=ConfigDict(extra='forbid')
    state_type: StateType | None=None
    value: StateValue | None=None
    interpretation_confidence: float=Field(default=0,ge=0,le=1)
    entity_candidates: list[EntityCandidate]=Field(default_factory=list)
    selected_entity_id: str | None=None
    requires_clarification: bool=False
    clarification_question: str | None=None
    used_ai: bool=False


class WitnessService:
    def __init__(self, *, entities: EntityResolutionService, observations: ObservationService, deterministic: DeterministicInterpreter, ai: AIInterpretationPort | None, evidence_store: EvidenceStorePort | None=None) -> None:
        self.entities=entities;self.observations=observations;self.deterministic=deterministic;self.ai=ai;self.evidence_store=evidence_store

    async def interpret(self, *, text: str, latitude: float | None=None, longitude: float | None=None) -> WitnessInterpretationResult:
        interpreted=self.deterministic.interpret(text);used_ai=False
        if not interpreted and self.ai:
            try: interpreted=await self.ai.interpret(text=text,latitude=latitude,longitude=longitude);used_ai=True
            except ExternalDependencyUnavailable: interpreted=None
        resolution=await self.entities.resolve(text=text,latitude=latitude,longitude=longitude)
        if not interpreted:
            return WitnessInterpretationResult(entity_candidates=resolution.candidates,selected_entity_id=resolution.selected_entity_id,requires_clarification=True,clarification_question='What is happening there now?',used_ai=used_ai)
        requires=interpreted.requires_clarification or (resolution.status!=EntityResolutionStatus.RESOLVED)
        question=interpreted.clarification_question
        if requires and not question: question='Which place, service, or object do you mean?' if resolution.candidates else 'Where did this happen?'
        return WitnessInterpretationResult(state_type=interpreted.state_type,value=interpreted.value,interpretation_confidence=interpreted.confidence,entity_candidates=resolution.candidates,selected_entity_id=resolution.selected_entity_id,requires_clarification=requires,clarification_question=question,used_ai=used_ai)

    async def report(self, principal: Principal, *, text: str, observed_at, entity_id: str | None=None, object_key: str='main', state_type: StateType | None=None, value: StateValue | None=None, latitude: float | None=None, longitude: float | None=None, location_accuracy_m: float | None=None, location_description: str | None=None):
        interpretation=await self.interpret(text=text,latitude=latitude,longitude=longitude) if (state_type is None or value is None or entity_id is None) else None
        resolved_entity=entity_id or (interpretation.selected_entity_id if interpretation else None)
        resolved_type=state_type or (interpretation.state_type if interpretation else None);resolved_value=value or (interpretation.value if interpretation else None)
        if not resolved_entity or not resolved_type or resolved_value is None: return interpretation,None
        observation=await self.observations.submit(principal,identity=StateIdentity(entity_id=resolved_entity,object_key=object_key,state_type=resolved_type),value=resolved_value,observed_at=observed_at,latitude=latitude,longitude=longitude,location_accuracy_m=location_accuracy_m,location_description=location_description,original_input_ref=text,interpretation_confidence=interpretation.interpretation_confidence if interpretation else 1.0)
        return interpretation,observation

    async def store_audio(self, *, data: bytes, content_type: str, file_name: str):
        if not self.evidence_store: raise ExternalDependencyUnavailable('evidence store is unavailable')
        return await self.evidence_store.put_bytes(data=data,content_type=content_type,suggested_name=file_name)
