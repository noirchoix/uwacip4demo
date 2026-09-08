from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from pipe4.domain.acquisition.models import DecisionContext
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import StateValue


class WatchStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ALERTING = "ALERTING"
    PAUSED = "PAUSED"


class WatchCondition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    identity: StateIdentity
    operator: str = Field(pattern="^(EQ|NEQ|GT|GTE|LT|LTE)$")
    target: StateValue
    decision_context: DecisionContext = Field(default_factory=DecisionContext)
    permission_scope_key: str = "default"


class WatchProcess(BaseModel):
    model_config = ConfigDict(extra="forbid")

    watch_process_id: str = Field(default_factory=lambda: str(uuid4()))
    fingerprint: str
    condition: WatchCondition
    created_at: datetime


class WatchSubscription(BaseModel):
    model_config = ConfigDict(extra="forbid")

    watch_id: str = Field(default_factory=lambda: str(uuid4()))
    watch_process_id: str
    subscriber_subject: str
    status: WatchStatus = WatchStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None
