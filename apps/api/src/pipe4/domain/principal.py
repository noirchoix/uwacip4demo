from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Principal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    subject: str
    roles: frozenset[str] = Field(default_factory=frozenset)
    permissions: frozenset[str] = Field(default_factory=frozenset)
    service: bool = False

    @property
    def authenticated(self) -> bool:
        return bool(self.subject)
