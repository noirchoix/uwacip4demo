from pipe4.domain.principal import Principal


class AllowAllUsageAdapter:
    async def allow(self, principal: Principal, *, operation: str, cost_units: int = 1) -> bool:
        return True
