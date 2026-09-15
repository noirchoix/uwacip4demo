from app.modules.current_state.domain.enums import AccessRequestStatus, StateLifecycle
from app.modules.current_state.domain.transitions import (
    access_transition_allowed,
    state_transition_allowed,
)


def test_replaced_state_cannot_become_current_again() -> None:
    assert not state_transition_allowed(StateLifecycle.REPLACED, StateLifecycle.CURRENT)


def test_current_state_can_be_disputed() -> None:
    assert state_transition_allowed(StateLifecycle.CURRENT, StateLifecycle.DISPUTED)


def test_approved_access_can_be_revoked() -> None:
    assert access_transition_allowed(AccessRequestStatus.APPROVED, AccessRequestStatus.REVOKED)


def test_denied_access_is_terminal() -> None:
    assert not access_transition_allowed(AccessRequestStatus.DENIED, AccessRequestStatus.APPROVED)
