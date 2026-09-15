import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.modules.current_state.domain.enums import WatchOperator, WatchStatus
from app.modules.current_state.domain.identity import StateIdentity

WatchTarget = str | int | float | bool | None
_NUMERIC_OPERATORS = {
    WatchOperator.LT,
    WatchOperator.LTE,
    WatchOperator.GT,
    WatchOperator.GTE,
}


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


class WatchCondition(BaseModel):
    """Canonical, aggregation-safe WATCH condition."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    identity: StateIdentity
    operator: WatchOperator
    target: WatchTarget
    field_path: str | None = None
    decision_context: str | None = None
    permission_tags: tuple[str, ...] = ()

    @field_validator("field_path")
    @classmethod
    def validate_field_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value or len(value) > 120:
            raise ValueError("field_path must contain 1 to 120 characters")
        return value

    @field_validator("decision_context")
    @classmethod
    def validate_decision_context(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value or len(value) > 80:
            raise ValueError("decision_context must contain 1 to 80 characters")
        return value

    @field_validator("permission_tags")
    @classmethod
    def sort_permission_tags(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(sorted(set(tag.strip() for tag in value)))
        if any(not tag for tag in normalized):
            raise ValueError("permission_tags cannot contain blank values")
        return normalized

    @model_validator(mode="after")
    def validate_operator_target(self) -> "WatchCondition":
        if isinstance(self.target, float) and not math.isfinite(self.target):
            raise ValueError("WATCH target must be a finite JSON scalar")
        if self.operator in _NUMERIC_OPERATORS:
            if isinstance(self.target, bool) or not isinstance(self.target, (int, float)):
                raise ValueError("threshold WATCH operators require a numeric target")
        return self

    @property
    def canonical_key(self) -> str:
        payload = {
            "identity_key": self.identity.key,
            "operator": self.operator.value,
            "target": self.target,
            "field_path": self.field_path,
            "decision_context": self.decision_context,
            "permission_tags": self.permission_tags,
        }
        return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class WatchSubscription:
    subscriber_user_id: UUID
    condition: WatchCondition
    created_at: datetime
    updated_at: datetime
    subscription_id: UUID = field(default_factory=uuid4)
    status: WatchStatus = WatchStatus.ACTIVE
    last_triggered_state_version_id: UUID | None = None
    last_condition_met: bool = False

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("WATCH timestamps must be timezone-aware")
