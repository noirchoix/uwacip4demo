from __future__ import annotations

import re

from pipe4.domain.entities.models import EntityCandidate, ReferenceEntity
from pipe4.domain.policies.nearby import distance_m
from pipe4.repositories.protocols import EntityRepository


class StandaloneEntityCatalog:
    def __init__(self, repository: EntityRepository, *, clock) -> None:
        self.repository = repository
        self.clock = clock

    async def get(self, entity_id: str) -> ReferenceEntity | None:
        return await self.repository.get_entity(entity_id)

    async def resolve(
        self,
        *,
        text: str,
        latitude: float | None,
        longitude: float | None,
        radius_m: int,
    ) -> list[EntityCandidate]:
        tokens = {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}
        rows = await self.repository.list_entities()
        candidates: list[EntityCandidate] = []
        for entity in rows:
            haystack = " ".join([entity.display_name, *entity.aliases]).lower()
            lexical = sum(1 for token in tokens if token in haystack)
            dist: float | None = None
            if (
                latitude is not None
                and longitude is not None
                and entity.latitude is not None
                and entity.longitude is not None
            ):
                dist = distance_m(latitude, longitude, entity.latitude, entity.longitude)
                if dist > radius_m:
                    continue
            lexical_score = min(1.0, lexical / max(1, len(tokens))) if tokens else 0.0
            distance_score = 0.5 if dist is None else max(0.0, 1 - dist / max(radius_m, 1))
            confidence = min(1.0, lexical_score * 0.7 + distance_score * 0.3)
            if confidence > 0.1 or not tokens:
                candidates.append(
                    EntityCandidate(
                        entity_id=entity.entity_id,
                        display_name=entity.display_name,
                        entity_type=entity.entity_type,
                        distance_m=dist,
                        confidence=confidence,
                    )
                )
        return sorted(candidates, key=lambda item: item.confidence, reverse=True)[:5]

    async def create_provisional(
        self,
        *,
        entity_type: str,
        display_name: str,
        latitude: float | None,
        longitude: float | None,
    ) -> ReferenceEntity:
        entity = ReferenceEntity(
            entity_type=entity_type,
            display_name=display_name,
            latitude=latitude,
            longitude=longitude,
            provisional=True,
            created_at=self.clock.now(),
        )
        return await self.repository.save_entity(entity)


class StandaloneLocator:
    def __init__(self, repository: EntityRepository) -> None:
        self.repository = repository

    async def nearby_entities(
        self, *, latitude: float, longitude: float, radius_m: int
    ) -> list[ReferenceEntity]:
        rows = await self.repository.list_entities()
        result: list[ReferenceEntity] = []
        for entity in rows:
            if entity.latitude is None or entity.longitude is None:
                continue
            if distance_m(latitude, longitude, entity.latitude, entity.longitude) <= radius_m:
                result.append(entity)
        return result
