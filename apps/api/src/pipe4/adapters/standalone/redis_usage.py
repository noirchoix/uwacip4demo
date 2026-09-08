from __future__ import annotations

import time

from redis.asyncio import Redis

from pipe4.config import Settings
from pipe4.domain.principal import Principal


class RedisUsageAdapter:
    def __init__(self, redis: Redis, settings: Settings) -> None:
        self.redis=redis; self.settings=settings

    def _limit(self, operation: str) -> int:
        if operation.startswith('witness'): return self.settings.rate_limit_witness_per_minute
        if operation=='nearby': return self.settings.rate_limit_nearby_per_minute
        if operation in {'state_request','provisional_entity','watch_create','access_request','targeted_response'}: return self.settings.rate_limit_mutation_per_minute
        return self.settings.rate_limit_default_per_minute

    async def allow(self, principal: Principal, *, operation: str, cost_units: int = 1) -> bool:
        if principal.service: return True
        bucket=int(time.time()//60);key=f'pipe4:rate:{operation}:{principal.subject}:{bucket}'
        value=await self.redis.incrby(key,max(1,cost_units))
        if value==max(1,cost_units): await self.redis.expire(key,120)
        return int(value)<=self._limit(operation)
