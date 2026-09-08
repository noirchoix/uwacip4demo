from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from pipe4.domain.state.enums import EpistemicStatus, StateType
from pipe4.exceptions import PolicyConfigurationError


class FreshnessPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    fresh_seconds: int = Field(gt=0)
    stale_grace_seconds: int = Field(ge=0)
    volatility: float = Field(ge=0, le=1)


class ConfidencePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    weights: dict[str, float]
    evidence_strengths: dict[str, float]
    source_type_baselines: dict[str, float]
    location_unknown_score: float = Field(ge=0, le=1)
    location_manual_score: float = Field(ge=0, le=1)
    location_gps_score: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_weights(self) -> "ConfidencePolicy":
        required = {"source_reliability", "evidence_quality", "corroboration", "recency", "location_quality"}
        if set(self.weights) != required:
            raise ValueError(f"confidence weights must be exactly {sorted(required)}")
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("confidence weights must sum to 1")
        if any(value < 0 or value > 1 for value in self.weights.values()):
            raise ValueError("confidence weights must be between 0 and 1")
        return self


class VerificationPolicyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    threshold: float = Field(ge=0, le=1)
    min_independent_origins: int = Field(ge=1)
    allowed_epistemic_statuses: set[EpistemicStatus]
    reject_inference_only: bool = True


class DecisionContextPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    minimum_confidence: float = Field(ge=0, le=1)
    allow_stale_grace: bool = False
    require_verified: bool = False


class SourceRankingPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    weights: dict[str, float]
    maximum_cost_units: float = Field(ge=0)
    maximum_latency_ms: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_weights(self) -> "SourceRankingPolicy":
        required = {"reliability", "authority", "evidence_capability", "latency", "cost"}
        if set(self.weights) != required:
            raise ValueError(f"source ranking weights must be exactly {sorted(required)}")
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("source ranking weights must sum to 1")
        return self


class NearbyRankingPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    weights: dict[str, float]
    default_radius_m: int = Field(gt=0)
    maximum_radius_m: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_weights(self) -> "NearbyRankingPolicy":
        required = {
            "proximity",
            "intent_relevance",
            "urgency",
            "uncertainty_consequence",
            "freshness",
            "confidence",
            "recent_change",
            "active_demand",
            "watch_relevance",
        }
        if set(self.weights) != required:
            raise ValueError(f"nearby weights must be exactly {sorted(required)}")
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("nearby weights must sum to 1")
        if self.default_radius_m > self.maximum_radius_m:
            raise ValueError("default nearby radius cannot exceed maximum")
        return self


class SourceLearningPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    prior_strength: float = Field(gt=0)
    minimum_reliability: float = Field(ge=0, le=1)
    maximum_reliability: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_bounds(self) -> "SourceLearningPolicy":
        if self.minimum_reliability > self.maximum_reliability:
            raise ValueError("minimum reliability cannot exceed maximum")
        return self


class StateTypePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    freshness: FreshnessPolicy
    allowed_value_kinds: set[str]
    material_equivalence_seconds: int = Field(ge=0)
    contradiction_minimum_confidence: float = Field(ge=0, le=1)
    verification: VerificationPolicyConfig


class PolicyBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    version: str
    state_types: dict[StateType, StateTypePolicy]
    confidence: ConfidencePolicy
    decision_contexts: dict[str, DecisionContextPolicy]
    source_ranking: SourceRankingPolicy
    nearby_ranking: NearbyRankingPolicy
    source_learning: SourceLearningPolicy

    @model_validator(mode="after")
    def require_five_state_types(self) -> "PolicyBundle":
        required = set(StateType)
        if set(self.state_types) != required:
            missing = sorted(x.value for x in required - set(self.state_types))
            extra = sorted(str(x) for x in set(self.state_types) - required)
            raise ValueError(f"state_types must define exactly five core domains; missing={missing}, extra={extra}")
        return self

    @property
    def content_hash(self) -> str:
        payload = self.model_dump(mode="json")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


def load_policy_bundle(path: Path) -> PolicyBundle:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return PolicyBundle.model_validate(raw)
    except Exception as exc:
        raise PolicyConfigurationError(f"invalid Pipe 4 policy bundle: {exc}") from exc
