from typing import Mapping, Protocol
from uuid import UUID


class NotificationPort(Protocol):
    async def notify(
        self,
        *,
        recipient_auth_user_id: UUID,
        notification_type: str,
        category: str,
        title: str,
        message: str,
        payload: Mapping[str, object],
        related_entity_type: str,
        related_entity_id: UUID,
        actor_id: UUID | None,
        correlation_id: str | None,
    ) -> None: ...
