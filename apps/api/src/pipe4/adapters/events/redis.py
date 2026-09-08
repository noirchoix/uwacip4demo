from __future__ import annotations

import json

from redis.asyncio import Redis

from pipe4.domain.events.models import DomainEvent


class RedisEventPublisher:
    def __init__(self, redis: Redis, *, channel: str='pipe4.events') -> None:
        self.redis=redis; self.channel=channel
    async def publish(self, event: DomainEvent) -> None:
        await self.redis.publish(self.channel,json.dumps(event.model_dump(mode='json'),sort_keys=True))
