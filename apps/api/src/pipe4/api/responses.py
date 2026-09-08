from __future__ import annotations
from fastapi import Request
from pipe4.api.envelope import ApiMeta, ApiSuccess

def success(request: Request, data):
    return ApiSuccess(data=data,meta=ApiMeta(request_id=request.state.request_id,timestamp=request.state.request_timestamp))
