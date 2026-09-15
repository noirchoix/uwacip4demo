from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.modules.current_state.domain.enums import StateType
from app.modules.current_state.domain.identity import StateIdentity
from app.modules.current_state.domain.nearby import NearbySignals, rank_nearby
from app.modules.current_state.domain.watch import WatchCondition

ENTITY = UUID("11111111-1111-4111-8111-111111111111")
NOW = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)


def test_watch_key_is_stable_for_permission_order() -> None:
    identity = StateIdentity(entity_id=ENTITY, state_type=StateType.AVAILABLE)
    first = WatchCondition(
        identity=identity,
        operator="eq",
        target=True,
        permission_tags=("b", "a"),
    )
    second = WatchCondition(
        identity=identity,
        operator="eq",
        target=True,
        permission_tags=("a", "b"),
    )
    assert first.canonical_key == second.canonical_key


def test_nearby_ranking_is_deterministic_and_separate_from_truth_confidence() -> None:
    signals = NearbySignals(
        distance_m=500,
        observed_at=NOW - timedelta(hours=1),
        verified=True,
        intent_match=0.8,
    )
    first = rank_nearby(signals, now=NOW)
    second = rank_nearby(signals, now=NOW)
    assert first == second
    assert 0 <= first.relevance_score <= 1
    assert {"proximity", "freshness", "verification", "intent"}.issubset(first.breakdown)
    assert first.policy_weights["proximity"] == 0.35
