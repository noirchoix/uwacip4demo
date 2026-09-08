from __future__ import annotations

import json
from typing import Annotated

from fastapi import Depends, Query, Request

from pipe4.domain.state.enums import StateType
from pipe4.domain.state.identity import StateIdentity
from pipe4.exceptions import Pipe4Error


def container(request: Request): return request.app.state.container


def state_identity(
    entity_id: Annotated[str, Query(min_length=1)],
    state_type: Annotated[StateType, Query()],
    object_key: Annotated[str, Query(min_length=1)]='main',
    location_key: Annotated[str | None, Query()]=None,
    qualifiers: Annotated[str | None, Query(description='JSON object of truth-defining qualifiers')]=None,
) -> StateIdentity:
    parsed={}
    if qualifiers:
        try:
            raw=json.loads(qualifiers)
            if not isinstance(raw,dict): raise ValueError
            parsed=raw
        except Exception as exc:
            raise Pipe4Error('qualifiers must be a JSON object') from exc
    return StateIdentity(entity_id=entity_id,object_key=object_key,state_type=state_type,location_key=location_key,qualifiers=parsed)
