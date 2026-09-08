from __future__ import annotations

import math
from dataclasses import dataclass

from .registry import PolicyRegistry


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@dataclass(frozen=True)
class NearbyFactors:
    proximity: float
    intent_relevance: float
    urgency: float
    uncertainty_consequence: float
    freshness: float
    confidence: float
    recent_change: float
    active_demand: float
    watch_relevance: float


class NearbyRankingEngine:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.policies = policies

    def score(self, factors: NearbyFactors) -> float:
        weights = self.policies.bundle.nearby_ranking.weights
        raw = sum(getattr(factors, name) * weight for name, weight in weights.items())
        return max(0.0, min(1.0, raw))
