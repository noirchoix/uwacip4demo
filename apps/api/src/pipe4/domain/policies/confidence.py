from __future__ import annotations

from datetime import datetime

from pipe4.domain.evidence.models import EvidenceRef, SourceProfile
from pipe4.domain.observation.models import LocationEvidenceType
from pipe4.domain.state.models import ConfidenceBreakdown

from .corroboration import CorroborationEngine
from .registry import PolicyRegistry


class ConfidenceEngine:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.policies = policies
        self.corroboration = CorroborationEngine()

    def calculate(
        self,
        *,
        state_type: str,
        sources: list[SourceProfile],
        evidence: list[EvidenceRef],
        observed_at: datetime,
        now: datetime,
        location_type: LocationEvidenceType = LocationEvidenceType.UNKNOWN,
    ) -> ConfidenceBreakdown:
        config = self.policies.bundle.confidence
        freshness = self.policies.state_type(state_type).freshness

        source_reliability = (
            sum(source.reliability for source in sources) / len(sources) if sources else 0.0
        )

        strengths = [
            config.evidence_strengths.get(item.evidence_class.value, 0.0) for item in evidence
        ]
        evidence_quality = sum(strengths) / len(strengths) if strengths else 0.0

        independent = self.corroboration.independent_origin_count(evidence)
        corroboration = min(1.0, independent / 2.0)

        age = max(0.0, (now - observed_at).total_seconds())
        recency = max(0.0, min(1.0, 1 - age / max(freshness.fresh_seconds, 1)))

        location_quality = {
            LocationEvidenceType.GPS_CONFIRMED: config.location_gps_score,
            LocationEvidenceType.MANUALLY_DESCRIBED: config.location_manual_score,
            LocationEvidenceType.UNKNOWN: config.location_unknown_score,
        }[location_type]

        factors = {
            "source_reliability": source_reliability,
            "evidence_quality": evidence_quality,
            "corroboration": corroboration,
            "recency": recency,
            "location_quality": location_quality,
        }
        score = sum(factors[name] * weight for name, weight in config.weights.items())
        score = max(0.0, min(1.0, score))

        return ConfidenceBreakdown(
            **factors,
            weighted_score=score,
            policy_version=self.policies.bundle.version,
        )
