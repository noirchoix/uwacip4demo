from app.modules.current_state.domain.enums import VerificationStatus
from app.modules.current_state.services.resolution import (
    ResolutionEvidence,
    ResolutionPolicy,
    decide_promotion,
)


def test_verified_non_contradicted_evidence_can_publish() -> None:
    result = decide_promotion(
        ResolutionEvidence(
            verification_status=VerificationStatus.VERIFIED,
            independent_origin_count=1,
            contradicted=False,
        )
    )
    assert result.publish is True
    assert result.reason == "verified"


def test_contradiction_blocks_publication_even_if_verified() -> None:
    result = decide_promotion(
        ResolutionEvidence(
            verification_status=VerificationStatus.VERIFIED,
            independent_origin_count=3,
            contradicted=True,
        )
    )
    assert result.publish is False
    assert result.reason == "contradicted_evidence"


def test_unverified_corroboration_is_not_implicitly_authoritative() -> None:
    result = decide_promotion(
        ResolutionEvidence(
            verification_status=VerificationStatus.UNVERIFIED,
            independent_origin_count=5,
            contradicted=False,
        )
    )
    assert result.publish is False


def test_explicit_policy_can_allow_corroboration_threshold() -> None:
    result = decide_promotion(
        ResolutionEvidence(
            verification_status=VerificationStatus.UNVERIFIED,
            independent_origin_count=2,
            contradicted=False,
        ),
        policy=ResolutionPolicy(allow_unverified_corroboration=True),
    )
    assert result.publish is True
