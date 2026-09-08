from __future__ import annotations

import hashlib
import hmac

from pipe4.domain.evidence.models import EvidenceRef, SourceProfile
from pipe4.domain.policies.registry import PolicyRegistry
from pipe4.domain.state.enums import StateType


class StandaloneProvenanceAdapter:
    def __init__(self, *, secret: bytes = b"pipe4-dev-pseudonym-key") -> None:
        self._evidence: dict[str, EvidenceRef] = {}
        self._secret = secret

    async def get_evidence(self, evidence_ids: list[str]) -> list[EvidenceRef]:
        return [self._evidence[eid] for eid in evidence_ids if eid in self._evidence]

    async def save_evidence(self, evidence: EvidenceRef) -> None:
        self._evidence[evidence.evidence_id] = evidence

    async def public_source_labels(self, *, source_ids: list[str], context_key: str) -> list[str]:
        labels: list[str] = []
        for source_id in source_ids:
            digest = hmac.new(self._secret, f"{context_key}:{source_id}".encode(), hashlib.sha256).hexdigest()
            ordinal = int(digest[:8], 16) % 999 + 1
            labels.append(f"Witness {ordinal}")
        return list(dict.fromkeys(labels))


class StandaloneSourceRegistry:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.sources: dict[str, SourceProfile] = {}
        self.policies=policies
        self.outcomes: dict[tuple[str,str,StateType], tuple[int,int]] = {}

    async def get_source(self, source_id: str) -> SourceProfile | None:
        return self.sources.get(source_id)

    def _contextual(self, source: SourceProfile, *, entity_id: str, state_type: StateType) -> SourceProfile:
        correct,incorrect=self.outcomes.get((source.source_id,entity_id,state_type),(0,0))
        cfg=self.policies.bundle.source_learning
        reliability=(source.reliability*cfg.prior_strength+correct)/(cfg.prior_strength+correct+incorrect)
        reliability=max(cfg.minimum_reliability,min(cfg.maximum_reliability,reliability))
        return source.model_copy(update={'reliability':reliability,'correct_outcomes':correct,'incorrect_outcomes':incorrect})

    async def get_source_for_context(self, source_id: str, *, entity_id: str, state_type: StateType) -> SourceProfile | None:
        source=self.sources.get(source_id);return self._contextual(source,entity_id=entity_id,state_type=state_type) if source else None

    async def list_sources(self) -> list[SourceProfile]:
        return list(self.sources.values())

    async def list_sources_for_context(self, *, entity_id: str, state_type: StateType) -> list[SourceProfile]:
        return [self._contextual(source,entity_id=entity_id,state_type=state_type) for source in self.sources.values()]

    async def save_source(self, source: SourceProfile) -> None:
        self.sources[source.source_id] = source

    async def record_outcome(self, source_id: str, *, entity_id: str, state_type: StateType, correct: bool) -> SourceProfile:
        source=self.sources[source_id];key=(source_id,entity_id,state_type);yes,no=self.outcomes.get(key,(0,0));self.outcomes[key]=(yes+(1 if correct else 0),no+(0 if correct else 1));return self._contextual(source,entity_id=entity_id,state_type=state_type)
