from typing import Protocol

from app.modules.current_state.schemas.contracts import WitnessInterpretation


class WitnessInterpretationPort(Protocol):
    async def interpret(self, *, text: str, object_hint: str | None) -> WitnessInterpretation: ...


class SpeechTranscriptionPort(Protocol):
    """Approved Core AI boundary required for Pipe 4 audio witness intake.

    Do not implement this by importing a provider SDK directly into current_state.
    """

    async def transcribe(self, *, audio: bytes, mime_type: str) -> str: ...
