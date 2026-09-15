from dataclasses import dataclass
from datetime import UTC, datetime

from app.modules.current_state.domain.enums import (
    EpistemicStatus,
    StateLifecycle,
    UserStateStatus,
)
from app.modules.current_state.domain.state import StateVersion


@dataclass(frozen=True, slots=True)
class PresentationDecision:
    status: UserStateStatus
    explanation: str


def user_status_for(
    state: StateVersion | None, *, now: datetime | None = None
) -> PresentationDecision:
    if state is None:
        return PresentationDecision(
            UserStateStatus.UNKNOWN,
            "No sufficiently supported current state is available.",
        )

    now = now or datetime.now(UTC)
    if state.expires_at is not None and state.expires_at <= now:
        return PresentationDecision(
            UserStateStatus.STALE,
            "The last known state has expired and should be revalidated.",
        )
    if state.lifecycle_status is StateLifecycle.DISPUTED:
        return PresentationDecision(
            UserStateStatus.DISPUTED,
            "Sources disagree about the current state.",
        )
    if state.lifecycle_status in {StateLifecycle.STALE, StateLifecycle.EXPIRED}:
        return PresentationDecision(UserStateStatus.STALE, "The last known state is stale.")
    if state.epistemic_status is EpistemicStatus.INFERRED:
        return PresentationDecision(
            UserStateStatus.INFERRED,
            "This state is inferred rather than directly observed.",
        )
    return PresentationDecision(
        UserStateStatus.CURRENT,
        "Current state is supported by the active resolution policy.",
    )
