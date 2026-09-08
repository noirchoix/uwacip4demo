from __future__ import annotations

from typing import Protocol

from pipe4.domain.events.models import DomainEvent


class EventPublisherPort(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
