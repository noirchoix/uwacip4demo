from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Depends, Request

from pipe4.api.auth import current_principal
from pipe4.domain.principal import Principal
from pipe4.exceptions import RateLimited


def usage_guard(operation: str, *, cost_units: int=1) -> Callable:
    async def guard(request: Request, principal: Annotated[Principal,Depends(current_principal)]) -> None:
        if not await request.app.state.container.usage.allow(principal,operation=operation,cost_units=cost_units):
            raise RateLimited('Too many requests. Please retry shortly.')
    return guard
