from __future__ import annotations

import hashlib
import json
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.current_state.domain.enums import StateType

ScalarQualifier = str | int | float | bool


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class StateIdentity(BaseModel):
    """Canonical identity of one reality claim.

    Requester identity, decision context and ordinary query preferences are intentionally excluded.
    Only facts that change what the truth *is* belong here.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entity_id: UUID
    object_key: str = Field(default="main", min_length=1, max_length=200)
    state_type: StateType
    location_key: str | None = Field(default=None, max_length=200)
    qualifiers: dict[str, ScalarQualifier] = Field(default_factory=dict)

    @field_validator("qualifiers")
    @classmethod
    def canonicalize_qualifiers(
        cls, value: dict[str, ScalarQualifier]
    ) -> dict[str, ScalarQualifier]:
        return dict(sorted(value.items()))

    @property
    def canonical_payload(self) -> dict[str, object]:
        return {
            "entity_id": str(self.entity_id),
            "object_key": self.object_key,
            "state_type": self.state_type.value,
            "location_key": self.location_key,
            "qualifiers": self.qualifiers,
        }

    @property
    def key(self) -> str:
        return hashlib.sha256(_canonical_json(self.canonical_payload).encode()).hexdigest()
