from __future__ import annotations

from typing import Protocol

from pipe4.domain.entities.models import EntityCandidate, ReferenceEntity


class EntityCatalogPort(Protocol):
    async def get(self, entity_id: str) -> ReferenceEntity | None: ...
    async def resolve(
        self,
        *,
        text: str,
        latitude: float | None,
        longitude: float | None,
        radius_m: int,
    ) -> list[EntityCandidate]: ...
    async def create_provisional(
        self,
        *,
        entity_type: str,
        display_name: str,
        latitude: float | None,
        longitude: float | None,
    ) -> ReferenceEntity: ...


class LocatorPort(Protocol):
    async def nearby_entities(
        self, *, latitude: float, longitude: float, radius_m: int
    ) -> list[ReferenceEntity]: ...
