from dataclasses import dataclass
from datetime import UTC, datetime


def _unit_interval(value: float, *, name: str) -> float:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


@dataclass(frozen=True, slots=True)
class NearbySignals:
    distance_m: float | None
    observed_at: datetime
    verified: bool
    intent_match: float
    urgency: float = 0.0
    consequence_of_uncertainty: float = 0.0
    confidence: float | None = None
    material_change_recency: float = 0.0
    active_demand: float = 0.0
    watch_relevance: float = 0.0

    def __post_init__(self) -> None:
        if self.distance_m is not None and self.distance_m < 0:
            raise ValueError("distance_m cannot be negative")
        if self.observed_at.tzinfo is None:
            raise ValueError("ranking timestamps must be timezone-aware")
        for name in (
            "intent_match",
            "urgency",
            "consequence_of_uncertainty",
            "material_change_recency",
            "active_demand",
            "watch_relevance",
        ):
            _unit_interval(getattr(self, name), name=name)
        if self.confidence is not None:
            _unit_interval(self.confidence, name="confidence")


@dataclass(frozen=True, slots=True)
class NearbyRankingPolicy:
    """Configurable horizontal relevance policy. Weights are not truth confidence.

    The defaults define the approved deterministic baseline. Additional requirement-defined
    signals are available but deliberately carry zero weight until product policy configures them.
    """

    proximity_weight: float = 0.35
    freshness_weight: float = 0.30
    verification_weight: float = 0.20
    intent_weight: float = 0.15
    urgency_weight: float = 0.0
    consequence_weight: float = 0.0
    confidence_weight: float = 0.0
    material_change_weight: float = 0.0
    active_demand_weight: float = 0.0
    watch_relevance_weight: float = 0.0
    max_distance_m: float = 5000.0
    freshness_horizon_seconds: float = 86400.0
    unknown_distance_score: float = 0.25
    unverified_score: float = 0.5
    unknown_confidence_score: float = 0.5

    def __post_init__(self) -> None:
        weights = self.weights
        if any(weight < 0 for weight in weights.values()):
            raise ValueError("Nearby ranking weights cannot be negative")
        if sum(weights.values()) <= 0:
            raise ValueError("Nearby ranking requires at least one positive weight")
        if self.max_distance_m <= 0 or self.freshness_horizon_seconds <= 0:
            raise ValueError("Nearby ranking distance/freshness horizons must be positive")
        _unit_interval(self.unknown_distance_score, name="unknown_distance_score")
        _unit_interval(self.unverified_score, name="unverified_score")
        _unit_interval(self.unknown_confidence_score, name="unknown_confidence_score")

    @property
    def weights(self) -> dict[str, float]:
        return {
            "proximity": self.proximity_weight,
            "freshness": self.freshness_weight,
            "verification": self.verification_weight,
            "intent": self.intent_weight,
            "urgency": self.urgency_weight,
            "consequence": self.consequence_weight,
            "confidence": self.confidence_weight,
            "material_change": self.material_change_weight,
            "active_demand": self.active_demand_weight,
            "watch_relevance": self.watch_relevance_weight,
        }


DEFAULT_NEARBY_RANKING_POLICY = NearbyRankingPolicy()


@dataclass(frozen=True, slots=True)
class NearbyRanking:
    relevance_score: float
    breakdown: dict[str, float]
    policy_weights: dict[str, float]


def rank_nearby(
    signals: NearbySignals,
    *,
    now: datetime | None = None,
    policy: NearbyRankingPolicy = DEFAULT_NEARBY_RANKING_POLICY,
) -> NearbyRanking:
    """Return deterministic discovery relevance, explicitly separate from truth confidence."""

    now = now or datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError("ranking timestamps must be timezone-aware")

    age_seconds = max(0.0, (now - signals.observed_at).total_seconds())
    freshness = max(
        0.0,
        1.0 - min(age_seconds / policy.freshness_horizon_seconds, 1.0),
    )
    if signals.distance_m is None:
        proximity = policy.unknown_distance_score
    else:
        proximity = max(
            0.0,
            1.0 - min(signals.distance_m / policy.max_distance_m, 1.0),
        )
    verification = 1.0 if signals.verified else policy.unverified_score
    confidence = (
        signals.confidence
        if signals.confidence is not None
        else policy.unknown_confidence_score
    )

    breakdown = {
        "proximity": round(proximity, 6),
        "freshness": round(freshness, 6),
        "verification": round(verification, 6),
        "intent": round(signals.intent_match, 6),
        "urgency": round(signals.urgency, 6),
        "consequence": round(signals.consequence_of_uncertainty, 6),
        "confidence": round(confidence, 6),
        "material_change": round(signals.material_change_recency, 6),
        "active_demand": round(signals.active_demand, 6),
        "watch_relevance": round(signals.watch_relevance, 6),
    }
    weights = policy.weights
    total_weight = sum(weights.values())
    score = sum(breakdown[name] * weight for name, weight in weights.items()) / total_weight
    return NearbyRanking(
        relevance_score=round(score, 6),
        breakdown=breakdown,
        policy_weights=dict(weights),
    )
