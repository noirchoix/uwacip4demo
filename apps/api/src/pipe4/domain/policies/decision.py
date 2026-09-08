from __future__ import annotations

from dataclasses import dataclass

from pipe4.domain.state.enums import VerificationStatus
from pipe4.domain.state.models import StateVersion

from .freshness import FreshnessAssessment
from .registry import PolicyRegistry


@dataclass(frozen=True)
class DecisionAssessment:
    acceptable: bool
    allow_stale: bool
    reason: str


class DecisionEngine:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.policies = policies

    def assess(
        self,
        *,
        state: StateVersion,
        freshness: FreshnessAssessment,
        decision_context: str,
    ) -> DecisionAssessment:
        policy = self.policies.decision_context(decision_context)
        if state.confidence < policy.minimum_confidence:
            return DecisionAssessment(False, False, "confidence below decision threshold")
        if policy.require_verified and state.verification_status != VerificationStatus.VERIFIED:
            return DecisionAssessment(False, False, "decision context requires verified state")
        if freshness.fresh:
            return DecisionAssessment(True, False, "fresh and admissible")
        if policy.allow_stale_grace and freshness.within_stale_grace:
            return DecisionAssessment(True, True, "explicit stale grace permitted")
        return DecisionAssessment(False, False, "freshness insufficient")
