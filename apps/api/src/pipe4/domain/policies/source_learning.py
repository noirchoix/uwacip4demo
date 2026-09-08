from __future__ import annotations

from pipe4.domain.evidence.models import SourceProfile

from .registry import PolicyRegistry


class SourceLearningPolicy:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.policies = policies

    def updated_reliability(self, source: SourceProfile, *, correct: bool) -> float:
        cfg = self.policies.bundle.source_learning
        correct_count = source.correct_outcomes + (1 if correct else 0)
        incorrect_count = source.incorrect_outcomes + (0 if correct else 1)
        prior_success = source.reliability * cfg.prior_strength
        value = (prior_success + correct_count) / (
            cfg.prior_strength + correct_count + incorrect_count
        )
        return max(cfg.minimum_reliability, min(cfg.maximum_reliability, value))
