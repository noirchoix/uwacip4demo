from __future__ import annotations

from typing import Protocol

from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import VisibilityScope
from pipe4.domain.state.identity import StateIdentity


class AuthorizationPort(Protocol):
    async def can_view(
        self,
        principal: Principal,
        *,
        identity: StateIdentity,
        visibility: VisibilityScope,
        permission_tags: set[str],
    ) -> bool: ...

    async def can_view_subject(
        self,
        subject: str,
        *,
        identity: StateIdentity,
        visibility: VisibilityScope,
        permission_tags: set[str],
    ) -> bool: ...

    async def can_declare(self, principal: Principal, *, entity_id: str) -> bool: ...
    async def can_verify(self, principal: Principal) -> bool: ...
    async def can_decide_access(self, principal: Principal, *, entity_id: str) -> bool: ...
    async def is_internal(self, principal: Principal) -> bool: ...
