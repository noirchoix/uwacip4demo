from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CurrentStateObservationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "current_state_observations"
    __table_args__ = (
        CheckConstraint(
            "(idempotency_key IS NULL AND idempotency_operation IS NULL "
            "AND idempotency_request_hash IS NULL) OR "
            "(actor_user_id IS NOT NULL AND idempotency_key IS NOT NULL "
            "AND idempotency_operation IS NOT NULL "
            "AND idempotency_request_hash IS NOT NULL)",
            name="ck_current_state_observation_idempotency_complete",
        ),
        UniqueConstraint(
            "actor_user_id",
            "idempotency_operation",
            "idempotency_key",
            name="uq_current_state_observation_actor_operation_key",
        ),
    )

    identity_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    object_key: Mapped[str] = mapped_column(String(200), nullable=False)
    state_type: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    location_key: Mapped[str | None] = mapped_column(String(200))
    qualifiers_json: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    value_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location_verification_status: Mapped[str] = mapped_column(String(32), nullable=False)
    location_description: Mapped[str | None] = mapped_column(Text)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), index=True
    )
    idempotency_operation: Mapped[str | None] = mapped_column(String(30))
    idempotency_key: Mapped[str | None] = mapped_column(String(128))
    idempotency_request_hash: Mapped[str | None] = mapped_column(String(64))
    correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)


class CurrentStateVersionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "current_state_versions"
    __table_args__ = (
        UniqueConstraint("identity_key", "version", name="uq_current_state_identity_version"),
    )

    identity_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    object_key: Mapped[str] = mapped_column(String(200), nullable=False)
    state_type: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    location_key: Mapped[str | None] = mapped_column(String(200))
    qualifiers_json: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    value_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    epistemic_status: Mapped[str] = mapped_column(String(32), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(24), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    visibility: Mapped[str] = mapped_column(String(24), nullable=False)
    predecessor_state_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("current_state_versions.id", ondelete="SET NULL")
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)


class CurrentStateVersionObservationModel(Base):
    __tablename__ = "current_state_version_observations"

    state_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("current_state_versions.id", ondelete="CASCADE"), primary_key=True
    )
    observation_id: Mapped[UUID] = mapped_column(
        ForeignKey("current_state_observations.id", ondelete="CASCADE"), primary_key=True
    )


class CurrentStateProjectionModel(TimestampMixin, Base):
    __tablename__ = "current_state_current_projection"

    identity_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    state_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("current_state_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )


class CurrentStateAccessRequestModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "current_state_access_requests"

    requester_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_entity_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    target_identity_key: Mapped[str | None] = mapped_column(String(64), index=True)
    requested_permission: Mapped[str] = mapped_column(String(24), nullable=False)
    requested_scope_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    approved_scope_json: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decision_actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), index=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_reason: Mapped[str | None] = mapped_column(String(500))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class CurrentStateWatchModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "current_state_watches"
    __table_args__ = (
        UniqueConstraint(
            "subscriber_user_id",
            "canonical_key",
            name="uq_current_state_watch_subscriber_key",
        ),
    )

    subscriber_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    canonical_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    condition_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    last_triggered_state_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("current_state_versions.id", ondelete="SET NULL")
    )
    last_condition_met: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CurrentStateAcquisitionRequestModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "current_state_acquisition_requests"

    identity_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_auth_user_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    what_to_confirm: Mapped[str] = mapped_column(String(500), nullable=False)
    approximate_distance_m: Mapped[float | None] = mapped_column(Float)
    reward_amount: Mapped[float | None] = mapped_column(Float)
    reward_currency: Mapped[str | None] = mapped_column(String(12))
    offered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    witness_session_id: Mapped[UUID | None] = mapped_column(Uuid)


class CurrentStateProvisionalEntityModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "current_state_provisional_entities"

    display_name: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), index=True
    )
    canonical_entity_id: Mapped[UUID | None] = mapped_column(Uuid, index=True)
    resolution_status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
