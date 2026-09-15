from dataclasses import dataclass

from app.modules.current_state.domain.enums import VerificationStatus


@dataclass(frozen=True, slots=True)
class ResolutionEvidence:
    verification_status: VerificationStatus
    independent_origin_count: int
    contradicted: bool


@dataclass(frozen=True, slots=True)
class ResolutionPolicy:
    min_independent_origins: int = 2
    allow_unverified_corroboration: bool = False


@dataclass(frozen=True, slots=True)
class PromotionDecision:
    publish: bool
    reason: str


def decide_promotion(
    evidence: ResolutionEvidence,
    *,
    policy: ResolutionPolicy = ResolutionPolicy(),
) -> PromotionDecision:
    if evidence.contradicted:
        return PromotionDecision(False, "contradicted_evidence")
    if evidence.verification_status is VerificationStatus.FAILED:
        return PromotionDecision(False, "verification_failed")
    if evidence.verification_status is VerificationStatus.VERIFIED:
        return PromotionDecision(True, "verified")
    if (
        policy.allow_unverified_corroboration
        and evidence.independent_origin_count >= policy.min_independent_origins
    ):
        return PromotionDecision(True, "policy_corroboration_threshold")
    return PromotionDecision(False, "verification_or_more_evidence_required")
