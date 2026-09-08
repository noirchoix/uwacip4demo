from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from pipe4.domain.evidence.models import EvidenceRef, SourceProfile
from pipe4.domain.policies.registry import PolicyRegistry
from pipe4.domain.policies.source_learning import SourceLearningPolicy

from . import models as db


class SqlProvenanceAdapter:
    def __init__(self, factory: async_sessionmaker[AsyncSession], *, secret: bytes) -> None:
        self.factory=factory; self.secret=secret

    async def get_evidence(self, evidence_ids: list[str]) -> list[EvidenceRef]:
        if not evidence_ids: return []
        async with self.factory() as session:
            rows=(await session.execute(select(db.EvidenceMetadataRow).where(db.EvidenceMetadataRow.evidence_id.in_(evidence_ids)))).scalars().all()
            return [EvidenceRef.model_validate({'evidence_id':r.evidence_id,'evidence_class':r.evidence_class,'source_id':r.source_id,'origin_key':r.origin_key,'content_hash':r.content_hash,'captured_at':r.captured_at,'received_at':r.received_at,'object_ref':r.object_ref,'metadata':r.evidence_metadata or {}}) for r in rows]

    async def save_evidence(self, evidence: EvidenceRef) -> None:
        async with self.factory() as session, session.begin():
            if not await session.get(db.EvidenceMetadataRow,evidence.evidence_id):
                session.add(db.EvidenceMetadataRow(evidence_id=evidence.evidence_id,evidence_class=evidence.evidence_class.value,source_id=evidence.source_id,origin_key=evidence.origin_key,content_hash=evidence.content_hash,captured_at=evidence.captured_at,received_at=evidence.received_at,object_ref=evidence.object_ref,evidence_metadata=evidence.metadata))

    async def public_source_labels(self, *, source_ids: list[str], context_key: str) -> list[str]:
        labels=[]
        for source_id in source_ids:
            digest=hmac.new(self.secret,f'{context_key}:{source_id}'.encode(),hashlib.sha256).hexdigest(); labels.append(f'Witness {int(digest[:8],16)%999+1}')
        return list(dict.fromkeys(labels))


class SqlSourceRegistry:
    def __init__(self, factory: async_sessionmaker[AsyncSession], policies: PolicyRegistry) -> None:
        self.factory=factory; self.policies=policies

    async def get_source(self, source_id: str) -> SourceProfile | None:
        async with self.factory() as session:
            r=await session.get(db.SourceProfileRow,source_id); return self._model(r) if r else None

    async def get_source_for_context(self, source_id: str, *, entity_id: str, state_type) -> SourceProfile | None:
        source=await self.get_source(source_id)
        if not source: return None
        return await self._contextual(source,entity_id=entity_id,state_type=state_type)

    async def list_sources(self) -> list[SourceProfile]:
        async with self.factory() as session:
            rows=(await session.execute(select(db.SourceProfileRow))).scalars().all(); return [self._model(r) for r in rows]

    async def list_sources_for_context(self, *, entity_id: str, state_type) -> list[SourceProfile]:
        return [await self._contextual(source,entity_id=entity_id,state_type=state_type) for source in await self.list_sources()]

    async def _contextual(self, source: SourceProfile, *, entity_id: str, state_type) -> SourceProfile:
        async with self.factory() as session:
            rows=(await session.execute(select(db.SourceReliabilityOutcomeRow.correct).where(db.SourceReliabilityOutcomeRow.source_id==source.source_id,db.SourceReliabilityOutcomeRow.entity_id==entity_id,db.SourceReliabilityOutcomeRow.state_type==state_type.value))).scalars().all()
        correct=sum(1 for v in rows if v);incorrect=len(rows)-correct;cfg=self.policies.bundle.source_learning
        reliability=(source.reliability*cfg.prior_strength+correct)/(cfg.prior_strength+correct+incorrect);reliability=max(cfg.minimum_reliability,min(cfg.maximum_reliability,reliability))
        return source.model_copy(update={'reliability':reliability,'correct_outcomes':correct,'incorrect_outcomes':incorrect})

    async def save_source(self, source: SourceProfile) -> None:
        async with self.factory() as session, session.begin():
            r=await session.get(db.SourceProfileRow,source.source_id,with_for_update=True); data=source.model_dump(mode='json'); data['authority_scopes']=list(source.authority_scopes)
            if r:
                for k,v in data.items(): setattr(r,k,v)
            else: session.add(db.SourceProfileRow(**data))

    async def record_outcome(self, source_id: str, *, entity_id: str, state_type, correct: bool) -> SourceProfile:
        async with self.factory() as session, session.begin():
            r=await session.get(db.SourceProfileRow,source_id,with_for_update=True)
            if not r: raise KeyError(source_id)
            source=self._model(r); before=await self._contextual(source,entity_id=entity_id,state_type=state_type)
            session.add(db.SourceReliabilityOutcomeRow(outcome_id=str(uuid4()),source_id=source_id,entity_id=entity_id,state_type=state_type.value,correct=correct,previous_reliability=before.reliability,new_reliability=before.reliability,recorded_at=datetime.now(timezone.utc)))
        # Re-query after the committed outcome and persist the resulting contextual value only in the outcome audit; global baseline remains stable.
        updated=await self._contextual(source,entity_id=entity_id,state_type=state_type)
        async with self.factory() as session, session.begin():
            row=(await session.execute(select(db.SourceReliabilityOutcomeRow).where(db.SourceReliabilityOutcomeRow.source_id==source_id,db.SourceReliabilityOutcomeRow.entity_id==entity_id,db.SourceReliabilityOutcomeRow.state_type==state_type.value).order_by(db.SourceReliabilityOutcomeRow.recorded_at.desc()).limit(1))).scalar_one();row.new_reliability=updated.reliability
        return updated

    @staticmethod
    def _model(r: db.SourceProfileRow) -> SourceProfile:
        return SourceProfile(source_id=r.source_id,source_type=r.source_type,authority_scopes=set(r.authority_scopes or []),reliability=r.reliability,evidence_capability=r.evidence_capability,expected_latency_ms=r.expected_latency_ms,cost_units=r.cost_units,provider_key=r.provider_key,correct_outcomes=r.correct_outcomes,incorrect_outcomes=r.incorrect_outcomes)
