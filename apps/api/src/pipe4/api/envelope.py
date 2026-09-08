from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T=TypeVar('T')

class ApiMeta(BaseModel):
    model_config=ConfigDict(extra='forbid')
    request_id: str
    timestamp: datetime

class ApiSuccess(BaseModel,Generic[T]):
    model_config=ConfigDict(extra='forbid')
    success: bool=True
    data: T
    meta: ApiMeta

class ApiErrorBody(BaseModel):
    model_config=ConfigDict(extra='forbid')
    code: str
    message: str
    details: dict[str,object] | None=None

class ApiFailure(BaseModel):
    model_config=ConfigDict(extra='forbid')
    success: bool=False
    error: ApiErrorBody
    meta: ApiMeta


STANDARD_ERRORS = {
    400: {"model": ApiFailure, "description": "Invalid request intent"},
    401: {"model": ApiFailure, "description": "Authentication required"},
    403: {"model": ApiFailure, "description": "Permission denied"},
    404: {"model": ApiFailure, "description": "Resource not found"},
    409: {"model": ApiFailure, "description": "State/resource conflict"},
    422: {"model": ApiFailure, "description": "Validation failed"},
    429: {"model": ApiFailure, "description": "Rate limited"},
    500: {"model": ApiFailure, "description": "Unexpected server error"},
    503: {"model": ApiFailure, "description": "Dependency unavailable"},
}
