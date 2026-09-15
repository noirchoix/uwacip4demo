import re
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.modules.current_state.domain.enums import (
    AccessPermission,
    AccessRequestStatus,
    StateType,
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _sorted_unique_strings(values: tuple[str, ...], *, field_name: str) -> tuple[str, ...]:
    normalized = tuple(sorted(set(values)))
    if any(not value.strip() for value in normalized):
        raise ValueError(f"{field_name} cannot contain blank values")
    return normalized


class AccessScope(BaseModel):
    """Typed descriptor of the read scope requested or approved for one target entity.

    Authorization evaluation remains an Identity/authorization responsibility.
    This value object makes Pipe 4 scope explicit and serializable without inventing a second
    permission engine.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    all_current_state: bool = False
    identity_keys: tuple[str, ...] = ()
    state_types: tuple[StateType, ...] = ()
    object_keys: tuple[str, ...] = ()
    field_paths: tuple[str, ...] = ()

    @field_validator("identity_keys")
    @classmethod
    def canonicalize_identity_keys(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = _sorted_unique_strings(values, field_name="identity_keys")
        for value in normalized:
            if len(value) != 64 or any(char not in "0123456789abcdefABCDEF" for char in value):
                raise ValueError("identity_keys must contain 64-character SHA-256 hex keys")
        return tuple(value.lower() for value in normalized)

    @field_validator("state_types")
    @classmethod
    def canonicalize_state_types(cls, values: tuple[StateType, ...]) -> tuple[StateType, ...]:
        return tuple(sorted(set(values), key=lambda item: item.value))

    @field_validator("object_keys", "field_paths")
    @classmethod
    def canonicalize_strings(cls, values: tuple[str, ...], info: object) -> tuple[str, ...]:
        field_name = getattr(info, "field_name", "scope")
        return _sorted_unique_strings(values, field_name=field_name)

    @model_validator(mode="after")
    def validate_scope_shape(self) -> "AccessScope":
        has_selectors = any(
            (self.identity_keys, self.state_types, self.object_keys, self.field_paths)
        )
        if self.all_current_state and has_selectors:
            raise ValueError("all_current_state cannot be combined with narrower selectors")
        if not self.all_current_state and not has_selectors:
            raise ValueError("access scope must identify at least one readable state dimension")
        return self

    def contains_scope(self, candidate: "AccessScope") -> bool:
        """Return whether candidate is no broader than this requested scope."""
        if self.all_current_state:
            return True
        if candidate.all_current_state:
            return False
        for requested_values, candidate_values in (
            (self.identity_keys, candidate.identity_keys),
            (self.state_types, candidate.state_types),
            (self.object_keys, candidate.object_keys),
            (self.field_paths, candidate.field_paths),
        ):
            if requested_values and (
                not candidate_values or not set(candidate_values).issubset(requested_values)
            ):
                return False
        return True


@dataclass(frozen=True, slots=True)
class AccessRequest:
    """Internal access-request record, separate from physical/current reality state."""

    requester_user_id: UUID
    target_entity_id: UUID
    requested_scope: AccessScope
    requested_at: datetime
    access_request_id: UUID = field(default_factory=uuid4)
    target_identity_key: str | None = None
    requested_permission: AccessPermission = AccessPermission.READ
    status: AccessRequestStatus = AccessRequestStatus.PENDING
    decision_actor_user_id: UUID | None = None
    decided_at: datetime | None = None
    decision_reason: str | None = None
    approved_scope: AccessScope | None = None
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        for value in (self.requested_at, self.decided_at, self.expires_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("access-request timestamps must be timezone-aware")
        if self.target_identity_key is not None:
            normalized_identity_key = self.target_identity_key.lower()
            if not _SHA256_RE.fullmatch(normalized_identity_key):
                raise ValueError("target_identity_key must be a 64-character SHA-256 hex key")
            object.__setattr__(self, "target_identity_key", normalized_identity_key)
        if len(self.decision_reason or "") > 500:
            raise ValueError("decision_reason cannot exceed 500 characters")
        decision_statuses = {
            AccessRequestStatus.APPROVED,
            AccessRequestStatus.DENIED,
            AccessRequestStatus.REVOKED,
        }
        if self.status in decision_statuses:
            if self.decision_actor_user_id is None or self.decided_at is None:
                raise ValueError("decided access requests require decision actor and timestamp")
        if self.status is AccessRequestStatus.APPROVED and self.approved_scope is None:
            raise ValueError("approved access request requires approved_scope")
        if (
            self.approved_scope is not None
            and not self.requested_scope.contains_scope(self.approved_scope)
        ):
            raise ValueError("approved_scope cannot broaden requested_scope")
        if self.status is AccessRequestStatus.DENIED and self.approved_scope is not None:
            raise ValueError("denied access request cannot grant approved_scope")
        if self.status is AccessRequestStatus.PENDING and any(
            (self.decision_actor_user_id, self.decided_at, self.approved_scope)
        ):
            raise ValueError("pending access request cannot contain decision/grant metadata")
