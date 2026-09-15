from app.modules.current_state.domain.enums import AccessRequestStatus, StateLifecycle

_STATE_ALLOWED: dict[StateLifecycle, frozenset[StateLifecycle]] = {
    StateLifecycle.CURRENT: frozenset({
        StateLifecycle.DISPUTED,
        StateLifecycle.STALE,
        StateLifecycle.EXPIRED,
        StateLifecycle.REPLACED,
    }),
    StateLifecycle.DISPUTED: frozenset({
        StateLifecycle.CURRENT,
        StateLifecycle.STALE,
        StateLifecycle.EXPIRED,
        StateLifecycle.REPLACED,
    }),
    StateLifecycle.STALE: frozenset({StateLifecycle.EXPIRED, StateLifecycle.REPLACED}),
    StateLifecycle.EXPIRED: frozenset({StateLifecycle.REPLACED}),
    StateLifecycle.REPLACED: frozenset(),
}

_ACCESS_ALLOWED: dict[AccessRequestStatus, frozenset[AccessRequestStatus]] = {
    AccessRequestStatus.PENDING: frozenset({
        AccessRequestStatus.APPROVED,
        AccessRequestStatus.DENIED,
        AccessRequestStatus.CANCELLED,
        AccessRequestStatus.EXPIRED,
    }),
    AccessRequestStatus.APPROVED: frozenset({
        AccessRequestStatus.REVOKED,
        AccessRequestStatus.EXPIRED,
    }),
    AccessRequestStatus.DENIED: frozenset(),
    AccessRequestStatus.REVOKED: frozenset(),
    AccessRequestStatus.EXPIRED: frozenset(),
    AccessRequestStatus.CANCELLED: frozenset(),
}


def state_transition_allowed(before: StateLifecycle, after: StateLifecycle) -> bool:
    return before == after or after in _STATE_ALLOWED[before]


def access_transition_allowed(before: AccessRequestStatus, after: AccessRequestStatus) -> bool:
    return before == after or after in _ACCESS_ALLOWED[before]
