from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import StateType


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class StateIdentity(BaseModel):
    """Truth identity for one horizontal state claim.

    Requester/decision context/ordinary requested quantity are intentionally excluded.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entity_id: str = Field(min_length=1, max_length=160)
    object_key: str = Field(default="main", min_length=1, max_length=200)
    state_type: StateType
    location_key: str | None = Field(default=None, max_length=200)
    qualifiers: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("qualifiers")
    @classmethod
    def canonicalize_qualifiers(
        cls, value: dict[str, str | int | float | bool]
    ) -> dict[str, str | int | float | bool]:
        return dict(sorted(value.items()))

    @property
    def canonical_payload(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "object_key": self.object_key,
            "state_type": self.state_type.value,
            "location_key": self.location_key,
            "qualifiers": self.qualifiers,
        }

    @property
    def key(self) -> str:
        return hashlib.sha256(_canonical_json(self.canonical_payload).encode("utf-8")).hexdigest()
