from __future__ import annotations

from typing import Protocol

from pipe4.domain.principal import Principal


class UsagePort(Protocol):
    async def allow(self, principal: Principal, *, operation: str, cost_units: int = 1) -> bool: ...
