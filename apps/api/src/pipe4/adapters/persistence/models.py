from __future__ import annotations

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class StateVersionRow(Base):
    __tablename__ = "state_version"

    state_version_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    identity_key: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(160), index=True)
    object_key: Mapped[str] = mapped_column(String(200))
    state_type: Mapped[str] = mapped_column(String(32), index=True)
    location_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    qualifiers: Mapped[dict] = mapped_column(JSON, default=dict)
    value: Mapped[dict] = mapped_column(JSON)
    epistemic_status: Mapped[str] = mapped_column(String(40))
    verification_status: Mapped[str] = mapped_column(String(40))
    lifecycle_status: Mapped[str] = mapped_column(String(40), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence: Mapped[float] = mapped_column(Float)
    confidence_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    policy_version: Mapped[str] = mapped_column(String(64))
    visibility: Mapped[str] = mapped_column(String(32))
    permission_tags: Mapped[list] = mapped_column(JSON, default=list)
    source_ids: Mapped[list] = mapped_column(JSON, default=list)
    evidence_ids: Mapped[list] = mapped_column(JSON, default=list)
    predecessor_state_version_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("state_version.state_version_id"), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer)
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    __table_args__ = (
        UniqueConstraint("identity_key", "version", name="uq_state_version_identity_version"),
        Index("ix_state_version_identity_created", "identity_key", "created_at"),
    )


class CurrentStateProjectionRow(Base):
    __tablename__ = "current_state_projection"

    identity_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    state_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("state_version.state_version_id"), unique=True
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ObservationRow(Base):
    __tablename__ = "observation"

    observation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    identity: Mapped[dict] = mapped_column(JSON)
    proposed_value: Mapped[dict] = mapped_column(JSON)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    actor_subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    epistemic_status: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_evidence_type: Mapped[str] = mapped_column(String(40))
    evidence_ids: Mapped[list] = mapped_column(JSON, default=list)
    original_input_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    interpretation_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    consumed_state_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class StateRequestRow(Base):
    __tablename__ = "state_request"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    identity: Mapped[dict] = mapped_column(JSON)
    identity_key: Mapped[str] = mapped_column(String(64), index=True)
    requester_subject: Mapped[str] = mapped_column(String(200))
    decision_context: Mapped[dict] = mapped_column(JSON)
    gap_reason: Mapped[str] = mapped_column(String(50))
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    demand_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_state_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class AcquisitionJobRow(Base):
    __tablename__ = "acquisition_job"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("state_request.request_id"), index=True)
    identity: Mapped[dict] = mapped_column(JSON)
    decision_context: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(40), index=True)
    candidate_source_ids: Mapped[list] = mapped_column(JSON, default=list)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AcquisitionAttemptRow(Base):
    __tablename__ = "acquisition_attempt"

    attempt_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("acquisition_job.job_id"), index=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    status: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_units: Mapped[float] = mapped_column(Float, default=0)
    result_observation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class WatchProcessRow(Base):
    __tablename__ = "watch_process"

    watch_process_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    condition: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WatchSubscriptionRow(Base):
    __tablename__ = "watch_subscription"

    watch_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    watch_process_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("watch_process.watch_process_id"), index=True
    )
    subscriber_subject: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccessRequestRow(Base):
    __tablename__ = "access_request"

    access_request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    requester_subject: Mapped[str] = mapped_column(String(200), index=True)
    target_entity_id: Mapped[str] = mapped_column(String(160), index=True)
    target_identity_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    requested_permission: Mapped[str] = mapped_column(String(50))
    requested_scope: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), index=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_by_subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    granted_scope: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PermissionGrantRow(Base):
    __tablename__ = "permission_grant"

    grant_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    access_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("access_request.access_request_id"), index=True)
    subject: Mapped[str] = mapped_column(String(200), index=True)
    target_entity_id: Mapped[str] = mapped_column(String(160), index=True)
    target_identity_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    permission: Mapped[str] = mapped_column(String(50))
    scope: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TargetedAcquisitionRow(Base):
    __tablename__ = "targeted_acquisition_request"

    targeted_request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    state_request_id: Mapped[str] = mapped_column(String(36), index=True)
    target_subject: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[str] = mapped_column(String(32))
    offered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_observation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reward_label: Mapped[str | None] = mapped_column(String(120), nullable=True)


class ContradictionRow(Base):
    __tablename__ = "contradiction"

    contradiction_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    identity_key: Mapped[str] = mapped_column(String(64), index=True)
    incumbent_state_version_id: Mapped[str] = mapped_column(String(36), index=True)
    competing_observation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    competing_state_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    material: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReferenceEntityRow(Base):
    __tablename__ = "reference_entity"

    entity_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(120), index=True)
    display_name: Mapped[str] = mapped_column(String(240), index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    provisional: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DomainEventRow(Base):
    __tablename__ = "domain_event"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    aggregate_type: Mapped[str] = mapped_column(String(80), index=True)
    aggregate_id: Mapped[str] = mapped_column(String(160), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class OutboxRow(Base):
    __tablename__ = "outbox"

    outbox_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("domain_event.event_id"), unique=True)
    event_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


class EvidenceMetadataRow(Base):
    __tablename__ = "evidence_metadata"

    evidence_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    evidence_class: Mapped[str] = mapped_column(String(60), index=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    origin_key: Mapped[str] = mapped_column(String(200), index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    object_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidence_metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class StateEvidenceLinkRow(Base):
    __tablename__ = "state_evidence_link"

    state_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("state_version.state_version_id"), primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(36), ForeignKey("evidence_metadata.evidence_id"), primary_key=True)


class SourceProfileRow(Base):
    __tablename__ = "source_profile"

    source_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    authority_scopes: Mapped[list] = mapped_column(JSON, default=list)
    reliability: Mapped[float] = mapped_column(Float)
    evidence_capability: Mapped[float] = mapped_column(Float)
    expected_latency_ms: Mapped[int] = mapped_column(Integer, default=1000)
    cost_units: Mapped[float] = mapped_column(Float, default=0)
    provider_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    correct_outcomes: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_outcomes: Mapped[int] = mapped_column(Integer, default=0)


class SourceReliabilityOutcomeRow(Base):
    __tablename__ = "source_reliability_outcome"

    outcome_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(160), ForeignKey("source_profile.source_id"), index=True)
    entity_id: Mapped[str] = mapped_column(String(160), index=True)
    state_type: Mapped[str] = mapped_column(String(32), index=True)
    correct: Mapped[bool] = mapped_column(Boolean)
    previous_reliability: Mapped[float] = mapped_column(Float)
    new_reliability: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IdempotencyRow(Base):
    __tablename__ = "idempotency_record"

    scope: Mapped[str] = mapped_column(String(120), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(200), primary_key=True)
    result_id: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
