import re
from dataclasses import dataclass
from uuid import UUID

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class IdempotencyContext:
    """Host-aligned idempotency identity for a current-state write operation."""

    user_id: UUID
    operation: str
    key: str
    request_hash: str

    def __post_init__(self) -> None:
        if not self.operation.strip() or not 1 <= len(self.operation) <= 30:
            raise ValueError("idempotency operation must contain 1 to 30 non-blank characters")
        if not self.key.strip() or not 1 <= len(self.key) <= 128:
            raise ValueError("idempotency key must contain 1 to 128 non-blank characters")
        if not _SHA256_RE.fullmatch(self.request_hash):
            raise ValueError("idempotency request_hash must be lowercase SHA-256 hex")
