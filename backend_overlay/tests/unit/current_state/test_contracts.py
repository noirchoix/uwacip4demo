from datetime import UTC, datetime
from uuid import UUID

from app.modules.current_state.domain.enums import (
    EntityResolutionStatus,
    EpistemicStatus,
    StateLifecycle,
    StateType,
    VerificationStatus,
    VisibilityScope,
)
from app.modules.current_state.domain.identity import StateIdentity
from app.modules.current_state.domain.values import BooleanStateValue
from app.modules.current_state.schemas.contracts import (
    Pipe4Entity,
    Pipe4StateVersion,
    WitnessReportRequest,
)

ENTITY = UUID("11111111-1111-4111-8111-111111111111")
NOW = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)


def test_state_version_contract_allows_unknown_confidence_and_expiry() -> None:
    state = Pipe4StateVersion(
        state_version_id=UUID("22222222-2222-4222-8222-222222222222"),
        identity=StateIdentity(entity_id=ENTITY, state_type=StateType.WORKING),
        value=BooleanStateValue(value=True),
        lifecycle_status=StateLifecycle.CURRENT,
        epistemic_status=EpistemicStatus.OBSERVED,
        verification_status=VerificationStatus.UNVERIFIED,
        confidence=None,
        observed_at=NOW,
        expires_at=None,
        visibility=VisibilityScope.PUBLIC,
    )
    assert state.confidence is None
    assert state.expires_at is None


def test_witness_report_contract_can_begin_before_entity_resolution() -> None:
    report = WitnessReportRequest(text="The clinic is open now")
    assert report.entity_id is None


def test_entity_contract_distinguishes_provisional_identity() -> None:
    entity = Pipe4Entity(
        entity_id=ENTITY,
        entity_type="provisional",
        display_name="Clinic near the market",
        resolution_status=EntityResolutionStatus.PROVISIONAL,
        created_at=NOW,
    )
    assert entity.resolution_status.value == "PROVISIONAL"


def test_public_state_version_does_not_expose_internal_evidence_graph_ids() -> None:
    state = Pipe4StateVersion(
        state_version_id=UUID("22222222-2222-4222-8222-222222222223"),
        identity=StateIdentity(entity_id=ENTITY, state_type=StateType.WORKING),
        value=BooleanStateValue(value=True),
        lifecycle_status=StateLifecycle.CURRENT,
        epistemic_status=EpistemicStatus.OBSERVED,
        verification_status=VerificationStatus.VERIFIED,
        confidence=None,
        observed_at=NOW,
        expires_at=None,
        visibility=VisibilityScope.PUBLIC,
    )
    payload = state.model_dump()
    assert "source_ids" not in payload
    assert "evidence_ids" not in payload
    assert "observation_ids" not in payload
