from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Request, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from pipe4.config import Settings
from pipe4.domain.principal import Principal
from pipe4.exceptions import AuthenticationRequired, PermissionDenied

bearer_scheme=HTTPBearer(auto_error=False)
internal_scheme=APIKeyHeader(name='X-Internal-Token',auto_error=False)

@dataclass
class AuthVerifier:
    settings: Settings

    async def verify(self, token: str) -> Principal:
        try:
            if self.settings.jwt_jwks_url:
                client=PyJWKClient(self.settings.jwt_jwks_url,cache_keys=True)
                key=await asyncio.to_thread(client.get_signing_key_from_jwt,token)
                payload=jwt.decode(token,key.key,algorithms=['RS256','ES256'],audience=self.settings.jwt_audience,issuer=self.settings.jwt_issuer,options={'verify_aud':bool(self.settings.jwt_audience),'verify_iss':bool(self.settings.jwt_issuer)})
            elif self.settings.jwt_hs256_secret:
                payload=jwt.decode(token,self.settings.jwt_hs256_secret,algorithms=['HS256'],audience=self.settings.jwt_audience,issuer=self.settings.jwt_issuer,options={'verify_aud':bool(self.settings.jwt_audience),'verify_iss':bool(self.settings.jwt_issuer)})
            else: raise AuthenticationRequired('authentication is not configured')
        except jwt.PyJWTError as exc: raise AuthenticationRequired('invalid or expired bearer token') from exc
        subject=str(payload.get('sub') or '')
        if not subject: raise AuthenticationRequired('token subject is missing')
        app_meta=payload.get('app_metadata') if isinstance(payload.get('app_metadata'),dict) else {}
        roles_raw=payload.get('roles') or app_meta.get('roles') or []
        if isinstance(roles_raw,str): roles_raw=[roles_raw]
        perms_raw=payload.get('permissions') or app_meta.get('permissions') or []
        if isinstance(perms_raw,str): perms_raw=[perms_raw]
        return Principal(subject=subject,roles=frozenset(map(str,roles_raw)),permissions=frozenset(map(str,perms_raw)),service=bool(payload.get('service',False)))

async def current_principal(request: Request, credentials: Annotated[HTTPAuthorizationCredentials | None,Security(bearer_scheme)]) -> Principal:
    override=getattr(request.app.state,'principal_override',None)
    if override is not None: return override
    if not credentials: raise AuthenticationRequired('bearer authentication required')
    return await request.app.state.container.auth_verifier.verify(credentials.credentials)

async def internal_principal(request: Request, token: Annotated[str | None,Security(internal_scheme)]) -> Principal:
    if token != request.app.state.container.settings.internal_api_token: raise PermissionDenied('internal service token required')
    return Principal(subject='service:internal',roles=frozenset({'uwaci_internal'}),permissions=frozenset({'*'}),service=True)
