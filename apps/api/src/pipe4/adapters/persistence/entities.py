from __future__ import annotations

from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from pipe4.domain.entities.models import EntityCandidate, ReferenceEntity

from . import models as db


class SqlEntityCatalog:
    def __init__(self, factory: async_sessionmaker[AsyncSession], *, clock) -> None:
        self.factory=factory; self.clock=clock

    async def get(self, entity_id: str) -> ReferenceEntity | None:
        async with self.factory() as session:
            r=await session.get(db.ReferenceEntityRow,entity_id)
            return self._model(r) if r else None

    async def resolve(self, *, text: str, latitude: float | None, longitude: float | None, radius_m: int) -> list[EntityCandidate]:
        term=f"%{text.strip()}%"
        async with self.factory() as session:
            stmt=select(db.ReferenceEntityRow)
            if text.strip():
                stmt=stmt.where(or_(db.ReferenceEntityRow.display_name.ilike(term),func.cast(db.ReferenceEntityRow.aliases, String).ilike(term)))
            if latitude is not None and longitude is not None:
                point=cast(ST_SetSRID(ST_MakePoint(longitude,latitude),4326), Geography)
                stmt=stmt.where(ST_DWithin(cast(db.ReferenceEntityRow.geom, Geography),point,radius_m)).limit(10)
            else: stmt=stmt.limit(10)
            rows=(await session.execute(stmt)).scalars().all()
        candidates=[]
        for r in rows:
            lexical=1.0 if text.strip().lower() in r.display_name.lower() else 0.65
            dist=None
            if latitude is not None and longitude is not None and r.latitude is not None and r.longitude is not None:
                from pipe4.domain.policies.nearby import distance_m
                dist=distance_m(latitude,longitude,r.latitude,r.longitude)
            distance_score=0.5 if dist is None else max(0.0,1-dist/max(radius_m,1))
            candidates.append(EntityCandidate(entity_id=r.entity_id,display_name=r.display_name,entity_type=r.entity_type,distance_m=dist,confidence=min(1.0,lexical*0.75+distance_score*0.25)))
        return sorted(candidates,key=lambda x:x.confidence,reverse=True)[:5]

    async def create_provisional(self, *, entity_type: str, display_name: str, latitude: float | None, longitude: float | None) -> ReferenceEntity:
        entity=ReferenceEntity(entity_type=entity_type,display_name=display_name,latitude=latitude,longitude=longitude,provisional=True,created_at=self.clock.now())
        geom=f'SRID=4326;POINT({longitude} {latitude})' if latitude is not None and longitude is not None else None
        async with self.factory() as session, session.begin():
            session.add(db.ReferenceEntityRow(**entity.model_dump(mode='json'),geom=geom))
        return entity

    @staticmethod
    def _model(r: db.ReferenceEntityRow) -> ReferenceEntity:
        return ReferenceEntity(entity_id=r.entity_id,entity_type=r.entity_type,display_name=r.display_name,latitude=r.latitude,longitude=r.longitude,aliases=r.aliases or [],provisional=r.provisional,created_at=r.created_at)


class SqlLocator:
    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None: self.factory=factory
    async def nearby_entities(self, *, latitude: float, longitude: float, radius_m: int) -> list[ReferenceEntity]:
        point=cast(ST_SetSRID(ST_MakePoint(longitude,latitude),4326), Geography)
        async with self.factory() as session:
            rows=(await session.execute(select(db.ReferenceEntityRow).where(ST_DWithin(cast(db.ReferenceEntityRow.geom, Geography),point,radius_m)))).scalars().all()
            return [SqlEntityCatalog._model(r) for r in rows]
