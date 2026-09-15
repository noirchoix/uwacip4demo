from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.modules.current_state.domain.enums import (
    EpistemicStatus,
    StateLifecycle,
    StateType,
    VerificationStatus,
)
from app.modules.current_state.domain.identity import StateIdentity
from app.modules.current_state.domain.state import StateVersion
from app.modules.current_state.domain.values import BooleanStateValue
from app.modules.current_state.services.presentation import user_status_for

NOW = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)
ENTITY = UUID("11111111-1111-4111-8111-111111111111")


def _state(**updates: object) -> StateVersion:
    payload = dict(
        identity=StateIdentity(entity_id=ENTITY, state_type=StateType.WORKING),
        value=BooleanStateValue(value=True),
        epistemic_status=EpistemicStatus.OBSERVED,
        verification_status=VerificationStatus.VERIFIED,
        observed_at=NOW - timedelta(minutes=5),
        valid_from=NOW - timedelta(minutes=5),
        created_at=NOW - timedelta(minutes=5),
    )
    payload.update(updates)
    return StateVersion(**payload)


def test_missing_state_is_unknown() -> None:
    assert user_status_for(None, now=NOW).status.value == "UNKNOWN"


def test_disputed_state_stays_disputed() -> None:
    state = _state(lifecycle_status=StateLifecycle.DISPUTED)
    assert user_status_for(state, now=NOW).status.value == "DISPUTED"


def test_expired_timestamp_is_presented_as_stale() -> None:
    state = _state(expires_at=NOW - timedelta(seconds=1))
    assert user_status_for(state, now=NOW).status.value == "STALE"
