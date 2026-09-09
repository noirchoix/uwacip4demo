from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EvidenceClass(StrEnum):
    OWNER_DECLARATION = "OWNER_DECLARATION"
    WITNESS_REPORT = "WITNESS_REPORT"
    INSTITUTIONAL_API = "INSTITUTIONAL_API"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    TRANSACTION_TRACE = "TRANSACTION_TRACE"
    SENSOR_READING = "SENSOR_READING"
    MEDIA = "MEDIA"
    DOCUMENT = "DOCUMENT"


class EvidenceRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    evidence_class: EvidenceClass
    source_id: str
    origin_key: str
    content_hash: str
    captured_at: datetime
    received_at: datetime
    object_ref: str | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class SourceProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_type: str
    authority_scopes: set[str] = Field(default_factory=set)
    reliability: float = Field(default=0.5, ge=0, le=1)
    evidence_capability: float = Field(default=0.5, ge=0, le=1)
    expected_latency_ms: int = Field(default=1000, ge=0)
    cost_units: float = Field(default=0.0, ge=0)
    provider_key: str | None = None
    correct_outcomes: int = Field(default=0, ge=0)
    incorrect_outcomes: int = Field(default=0, ge=0)
