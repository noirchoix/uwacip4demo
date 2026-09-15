from typing import Protocol
from uuid import UUID

from app.modules.current_state.schemas.contracts import EntityResolutionResult, Pipe4Entity


class EntityDirectoryPort(Protocol):
    async def resolve(
        self,
        *,
        query: str,
        latitude: float | None,
        longitude: float | None,
        radius_m: int,
    ) -> EntityResolutionResult: ...
    async def get(self, entity_id: UUID) -> Pipe4Entity | None: ...
