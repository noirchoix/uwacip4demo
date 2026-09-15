from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.modules.current_state.domain.access import AccessRequest
from app.modules.current_state.domain.idempotency import IdempotencyContext
from app.modules.current_state.domain.observation import ObservationRecord
from app.modules.current_state.domain.state import StateVersion
from app.modules.current_state.domain.watch import WatchSubscription


class IdempotencyConflictError(RuntimeError):
    """Same principal/operation/key was reused with a different request payload."""


class ConcurrentStatePublicationError(RuntimeError):
    """Current projection changed after the caller resolved its candidate state version."""


@dataclass(frozen=True, slots=True)
class ObservationWriteResult:
    observation: ObservationRecord
    replayed: bool


class CurrentStateRepository(Protocol):
    async def add_observation(
        self,
        observation: ObservationRecord,
        *,
        idempotency: IdempotencyContext | None = None,
    ) -> ObservationWriteResult:
        """Persist once; replay same-hash duplicates and reject key reuse with different payload."""
        ...

    async def get_observation(
        self, observation_id: UUID
    ) -> ObservationRecord | None: ...

    async def publish_state_version(
        self,
        state: StateVersion,
        *,
        expected_current_state_version_id: UUID | None,
    ) -> StateVersion:
        """Atomically append history and advance the current projection.

        Implementations must check the expected current version inside the same transaction/lock
        used to insert the new version. The new state predecessor must match that expected version;
        a mismatch raises ConcurrentStatePublicationError before either history or projection
        changes.
        """
        ...

    async def get_current_state(self, identity_key: str) -> StateVersion | None: ...

    async def list_state_history(
        self, identity_key: str, *, limit: int
    ) -> tuple[StateVersion, ...]: ...

    async def create_access_request(self, request: AccessRequest) -> AccessRequest: ...
    async def save_watch(self, watch: WatchSubscription) -> WatchSubscription: ...
