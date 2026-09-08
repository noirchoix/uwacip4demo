from __future__ import annotations

from enum import StrEnum


class StateType(StrEnum):
    AVAILABLE = "AVAILABLE"
    ACCESSIBLE = "ACCESSIBLE"
    WORKING = "WORKING"
    TIME = "TIME"
    CHANGED = "CHANGED"


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


class PublishedStateLifecycle(StrEnum):
    CURRENT = "CURRENT"
    DISPUTED = "DISPUTED"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    REPLACED = "REPLACED"


class UserFacingStateStatus(StrEnum):
    CURRENT = "CURRENT"
    VERIFYING = "VERIFYING"
    DISPUTED = "DISPUTED"
    STALE = "STALE"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class PresentationKind(StrEnum):
    STATE = "STATE"
    PROTECTED = "PROTECTED"
    UNKNOWN = "UNKNOWN"


class VisibilityScope(StrEnum):
    PUBLIC = "PUBLIC"
    TARGETED = "TARGETED"
    PRIVATE = "PRIVATE"
    INSTITUTIONAL = "INSTITUTIONAL"
    INTERNAL = "INTERNAL"
