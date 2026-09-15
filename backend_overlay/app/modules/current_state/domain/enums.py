from enum import StrEnum


class StateType(StrEnum):
    AVAILABLE = "AVAILABLE"
    ACCESSIBLE = "ACCESSIBLE"
    WORKING = "WORKING"
    TIME = "TIME"
    CHANGED = "CHANGED"


class RequestLifecycle(StrEnum):
    REQUESTED = "REQUESTED"
    ACQUIRING = "ACQUIRING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class ObservationStatus(StrEnum):
    RECEIVED = "RECEIVED"
    INTERPRETED = "INTERPRETED"
    ENTITY_RESOLVED = "ENTITY_RESOLVED"
    ACCEPTED_AS_EVIDENCE = "ACCEPTED_AS_EVIDENCE"
    VERIFYING = "VERIFYING"
    CONSUMED = "CONSUMED"
    REJECTED = "REJECTED"


class EpistemicStatus(StrEnum):
    DECLARED = "DECLARED"
    OBSERVED = "OBSERVED"
    SYSTEM_REPORTED = "SYSTEM_REPORTED"
    TRANSACTION_EVIDENCED = "TRANSACTION_EVIDENCED"
    INFERRED = "INFERRED"
    VERIFIED = "VERIFIED"


class VerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


class StateLifecycle(StrEnum):
    CURRENT = "CURRENT"
    DISPUTED = "DISPUTED"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    REPLACED = "REPLACED"


class UserStateStatus(StrEnum):
    CURRENT = "CURRENT"
    VERIFYING = "VERIFYING"
    DISPUTED = "DISPUTED"
    STALE = "STALE"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class VisibilityScope(StrEnum):
    PUBLIC = "PUBLIC"
    TARGETED = "TARGETED"
    PRIVATE = "PRIVATE"
    INSTITUTIONAL = "INSTITUTIONAL"
    INTERNAL = "INTERNAL"


class LocationVerificationStatus(StrEnum):
    GPS_CONFIRMED = "GPS_CONFIRMED"
    MANUAL_DESCRIPTION = "MANUAL_DESCRIPTION"
    UNKNOWN = "UNKNOWN"


class EntityResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    PROVISIONAL = "PROVISIONAL"
    MERGED = "MERGED"
    REJECTED = "REJECTED"


class AccessPermission(StrEnum):
    """MVP permission vocabulary for protected current-state reads.

    Approval of READ does not confer declaration, observation, verification, or mutation rights.
    """

    READ = "READ"


class AccessRequestStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class WatchOperator(StrEnum):
    """Small, explicit WATCH operator set for the MVP.

    Values intentionally match the existing mobile lowercase convention while the backend narrows
    an open-ended string contract.
    """

    EQ = "eq"
    NE = "ne"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    CHANGED_TO = "changed_to"


class WatchStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ALERTING = "ALERTING"
    PAUSED = "PAUSED"


class TargetedAcquisitionStatus(StrEnum):
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"
