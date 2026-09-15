from datetime import datetime
from typing import Protocol
from uuid import UUID


class KnowledgePort(Protocol):
    async def attach_observation_provenance(
        self,
        *,
        observation_id: UUID,
        source_type: str,
        source_reference: str | None,
        supplier_identity: str | None,
        observed_at: datetime,
        confidence: float | None,
        actor_user_id: UUID | None,
        correlation_id: str | None,
    ) -> UUID: ...

    async def public_source_labels(self, observation_ids: tuple[UUID, ...]) -> tuple[str, ...]: ...
