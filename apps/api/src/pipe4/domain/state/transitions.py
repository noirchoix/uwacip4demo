from __future__ import annotations

from pipe4.domain.state.enums import PublishedStateLifecycle
from pipe4.exceptions import InvalidTransition

_ALLOWED: dict[PublishedStateLifecycle, set[PublishedStateLifecycle]] = {
    PublishedStateLifecycle.CURRENT: {
        PublishedStateLifecycle.DISPUTED,
        PublishedStateLifecycle.STALE,
        PublishedStateLifecycle.EXPIRED,
        PublishedStateLifecycle.REPLACED,
    },
    PublishedStateLifecycle.DISPUTED: {
        PublishedStateLifecycle.CURRENT,
        PublishedStateLifecycle.STALE,
        PublishedStateLifecycle.EXPIRED,
        PublishedStateLifecycle.REPLACED,
    },
    PublishedStateLifecycle.STALE: {
        PublishedStateLifecycle.EXPIRED,
        PublishedStateLifecycle.REPLACED,
    },
    PublishedStateLifecycle.EXPIRED: {PublishedStateLifecycle.REPLACED},
    PublishedStateLifecycle.REPLACED: set(),
}


def assert_published_transition(
    before: PublishedStateLifecycle, after: PublishedStateLifecycle
) -> None:
    if before == after:
        return
    if after not in _ALLOWED[before]:
        raise InvalidTransition(f"illegal published-state transition: {before.value} -> {after.value}")
