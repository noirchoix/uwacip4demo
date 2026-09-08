from __future__ import annotations

from pipe4.domain.entities.models import EntityResolutionResult, EntityResolutionStatus, ReferenceEntity
from pipe4.ports.entities import EntityCatalogPort


class EntityResolutionService:
    def __init__(self, catalog: EntityCatalogPort) -> None: self.catalog=catalog

    async def resolve(self, *, text: str, latitude: float | None=None, longitude: float | None=None, radius_m: int=5000) -> EntityResolutionResult:
        candidates=await self.catalog.resolve(text=text,latitude=latitude,longitude=longitude,radius_m=radius_m)
        if not candidates: return EntityResolutionResult(status=EntityResolutionStatus.UNRESOLVED)
        if len(candidates)==1 and candidates[0].confidence>=0.82: return EntityResolutionResult(status=EntityResolutionStatus.RESOLVED,candidates=candidates,selected_entity_id=candidates[0].entity_id)
        if candidates[0].confidence>=0.90 and (len(candidates)==1 or candidates[0].confidence-candidates[1].confidence>=0.20): return EntityResolutionResult(status=EntityResolutionStatus.RESOLVED,candidates=candidates,selected_entity_id=candidates[0].entity_id)
        return EntityResolutionResult(status=EntityResolutionStatus.AMBIGUOUS,candidates=candidates)

    async def provisional(self, *, entity_type: str, display_name: str, latitude: float | None=None, longitude: float | None=None) -> ReferenceEntity:
        return await self.catalog.create_provisional(entity_type=entity_type,display_name=display_name,latitude=latitude,longitude=longitude)
