from __future__ import annotations

from dataclasses import dataclass

from pipe4.domain.evidence.models import EvidenceRef
from pipe4.domain.state.enums import EpistemicStatus, VerificationStatus
from pipe4.domain.state.models import ConfidenceBreakdown

from .corroboration import CorroborationEngine
from .registry import PolicyRegistry


@dataclass(frozen=True)
class VerificationDecision:
    status: VerificationStatus
    reason: str


class VerificationPolicy:
    def __init__(self, policies: PolicyRegistry) -> None:
        self.policies = policies
        self.corroboration = CorroborationEngine()

    def evaluate(
        self,
        *,
        state_type: str,
        epistemic_status: EpistemicStatus,
        confidence: ConfidenceBreakdown,
        evidence: list[EvidenceRef],
        has_unresolved_material_contradiction: bool,
    ) -> VerificationDecision:
        policy = self.policies.state_type(state_type).verification
        if policy.reject_inference_only and epistemic_status == EpistemicStatus.INFERRED:
            return VerificationDecision(VerificationStatus.INCONCLUSIVE, "inference alone cannot verify reality")
        if epistemic_status not in policy.allowed_epistemic_statuses:
            return VerificationDecision(VerificationStatus.INCONCLUSIVE, "epistemic status is not eligible")
        if has_unresolved_material_contradiction:
            return VerificationDecision(VerificationStatus.INCONCLUSIVE, "material contradiction remains unresolved")
        independent = self.corroboration.independent_origin_count(evidence)
        if independent < policy.min_independent_origins:
            return VerificationDecision(VerificationStatus.INCONCLUSIVE, "insufficient independent evidence origins")
        if confidence.weighted_score < policy.threshold:
            return VerificationDecision(VerificationStatus.INCONCLUSIVE, "confidence below verification threshold")
        return VerificationDecision(VerificationStatus.VERIFIED, "named verification policy satisfied")
