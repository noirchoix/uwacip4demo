from __future__ import annotations

import re

from pipe4.domain.state.enums import StateType
from pipe4.domain.state.values import BooleanStateValue, DurationStateValue
from pipe4.ports.ai import AIInterpretation


class DeterministicInterpreter:
    """Small sufficient parser for high-signal expressions; no model required."""

    _minutes = re.compile(r"\b(?:wait(?:ing)?(?:\s+time)?(?:\s+is)?|about)\s+(\d{1,4})\s*(?:min|mins|minute|minutes)\b", re.I)

    def interpret(self, text: str) -> AIInterpretation | None:
        normalized = " ".join(text.lower().split())

        if any(phrase in normalized for phrase in ("not working", "isn't working", "is not working", "broken", "out of service")):
            return AIInterpretation(
                state_type=StateType.WORKING,
                value=BooleanStateValue(value=False),
                confidence=0.96,
            )
        if any(phrase in normalized for phrase in ("working now", "is working", "back online")):
            return AIInterpretation(
                state_type=StateType.WORKING,
                value=BooleanStateValue(value=True),
                confidence=0.93,
            )
        if any(phrase in normalized for phrase in ("not available", "sold out", "out of stock", "unavailable")):
            return AIInterpretation(
                state_type=StateType.AVAILABLE,
                value=BooleanStateValue(value=False),
                confidence=0.94,
            )
        if any(phrase in normalized for phrase in ("available now", "in stock", "is available")):
            return AIInterpretation(
                state_type=StateType.AVAILABLE,
                value=BooleanStateValue(value=True),
                confidence=0.91,
            )
        if any(phrase in normalized for phrase in ("closed", "blocked", "inaccessible")):
            return AIInterpretation(
                state_type=StateType.ACCESSIBLE,
                value=BooleanStateValue(value=False),
                confidence=0.91,
            )
        if any(phrase in normalized for phrase in ("open now", "accessible", "can enter")):
            return AIInterpretation(
                state_type=StateType.ACCESSIBLE,
                value=BooleanStateValue(value=True),
                confidence=0.88,
            )
        match = self._minutes.search(text)
        if match:
            return AIInterpretation(
                state_type=StateType.TIME,
                value=DurationStateValue(seconds=int(match.group(1)) * 60),
                confidence=0.93,
            )
        return None
