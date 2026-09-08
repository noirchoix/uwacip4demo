from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from pipe4.domain.state.enums import StateType
from pipe4.domain.state.values import StateValue


class AIInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_type: StateType | None = None
    value: StateValue | None = None
    entity_hint: str | None = None
    confidence: float = Field(default=0, ge=0, le=1)
    requires_clarification: bool = False
    clarification_question: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None


class AIInterpretationPort(Protocol):
    async def interpret(
        self,
        *,
        text: str,
        latitude: float | None,
        longitude: float | None,
    ) -> AIInterpretation: ...
