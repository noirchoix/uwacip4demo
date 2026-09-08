from __future__ import annotations

from dataclasses import dataclass

from pipe4.domain.evidence.models import SourceProfile
from pipe4.domain.state.enums import StateType

from .registry import PolicyRegistry


@dataclass(frozen=True)
class RankedSource:
    source: SourceProfile
    score: float


class SourceRankingEngine:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.policies = policies

    def rank(self, sources: list[SourceProfile], *, state_type: StateType) -> list[RankedSource]:
        policy = self.policies.bundle.source_ranking
        eligible = [
            source
            for source in sources
            if (
                (not source.authority_scopes or state_type.value in source.authority_scopes)
                and source.cost_units <= policy.maximum_cost_units
                and source.expected_latency_ms <= policy.maximum_latency_ms
            )
        ]

        ranked: list[RankedSource] = []
        for source in eligible:
            authority = 1.0 if state_type.value in source.authority_scopes else 0.5
            latency = max(0.0, 1 - source.expected_latency_ms / policy.maximum_latency_ms)
            cost = max(0.0, 1 - source.cost_units / max(policy.maximum_cost_units, 1e-9))
            score = (
                source.reliability * policy.weights["reliability"]
                + authority * policy.weights["authority"]
                + source.evidence_capability * policy.weights["evidence_capability"]
                + latency * policy.weights["latency"]
                + cost * policy.weights["cost"]
            )
            ranked.append(RankedSource(source, score))
        return sorted(ranked, key=lambda item: item.score, reverse=True)
