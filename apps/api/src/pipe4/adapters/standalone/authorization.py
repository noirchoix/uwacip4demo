from __future__ import annotations

from pipe4.domain.principal import Principal
from pipe4.domain.state.enums import VisibilityScope
from pipe4.domain.state.identity import StateIdentity
from pipe4.ports.authorization import AuthorizationPort
from pipe4.repositories.protocols import AccessRepository


class StandaloneAuthorizationAdapter(AuthorizationPort):
    def __init__(self, access: AccessRepository) -> None:
        self.access = access

    async def can_view(
        self,
        principal: Principal,
        *,
        identity: StateIdentity,
        visibility: VisibilityScope,
        permission_tags: set[str],
    ) -> bool:
        if visibility == VisibilityScope.PUBLIC:
            return True
        if await self.is_internal(principal):
            return True
        if permission_tags and principal.permissions.intersection(permission_tags):
            return True
        return await self.access.has_grant(
            subject=principal.subject,
            entity_id=identity.entity_id,
            identity_key=identity.key,
            permission='READ',
        )

    async def can_view_subject(
        self,
        subject: str,
        *,
        identity: StateIdentity,
        visibility: VisibilityScope,
        permission_tags: set[str],
    ) -> bool:
        if visibility == VisibilityScope.PUBLIC:
            return True
        return await self.access.has_grant(
            subject=subject,
            entity_id=identity.entity_id,
            identity_key=identity.key,
            permission='READ',
        )

    async def can_declare(self, principal: Principal, *, entity_id: str) -> bool:
        return await self.is_internal(principal) or 'owner' in principal.roles or 'operator' in principal.roles

    async def can_verify(self, principal: Principal) -> bool:
        return await self.is_internal(principal) or 'verifier' in principal.roles

    async def can_decide_access(self, principal: Principal, *, entity_id: str) -> bool:
        return await self.is_internal(principal) or bool(
            principal.roles.intersection({'owner', 'operator', 'institution_admin'})
        )

    async def is_internal(self, principal: Principal) -> bool:
        return principal.service or 'uwaci_internal' in principal.roles
