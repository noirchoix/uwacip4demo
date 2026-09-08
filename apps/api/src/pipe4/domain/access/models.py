from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class AccessRequestStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class AccessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_request_id: str = Field(default_factory=lambda: str(uuid4()))
    requester_subject: str
    target_entity_id: str
    target_identity_key: str | None = None
    requested_permission: str = "READ"
    requested_scope: dict[str, str | int | float | bool] = Field(default_factory=dict)
    status: AccessRequestStatus = AccessRequestStatus.PENDING
    requested_at: datetime
    decided_at: datetime | None = None
    decided_by_subject: str | None = None
    decision_reason: str | None = None
    granted_scope: dict[str, str | int | float | bool] | None = None
    expires_at: datetime | None = None


class PermissionGrant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grant_id: str = Field(default_factory=lambda: str(uuid4()))
    access_request_id: str
    subject: str
    target_entity_id: str
    target_identity_key: str | None = None
    permission: str = "READ"
    scope: dict[str, str | int | float | bool] = Field(default_factory=dict)
    created_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
