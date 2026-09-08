from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pipe4.domain.state.models import StateVersion

from .registry import PolicyRegistry


@dataclass(frozen=True)
class FreshnessAssessment:
    fresh: bool
    within_stale_grace: bool
    age_seconds: int
    freshness_score: float


class FreshnessEngine:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.policies = policies

    def assess(self, state: StateVersion, *, now: datetime) -> FreshnessAssessment:
        policy = self.policies.state_type(state.identity.state_type).freshness
        age_seconds = max(0, int((now - state.observed_at).total_seconds()))
        fresh = age_seconds <= policy.fresh_seconds
        within_grace = age_seconds <= policy.fresh_seconds + policy.stale_grace_seconds
        freshness_score = max(0.0, min(1.0, 1 - age_seconds / max(policy.fresh_seconds, 1)))
        return FreshnessAssessment(fresh, within_grace, age_seconds, freshness_score)
