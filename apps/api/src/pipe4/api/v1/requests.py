from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.usage import usage_guard
from pipe4.api.schemas import RevalidateRequest, StateRequestBody
from pipe4.domain.acquisition.models import GapReason, StateRequest
from pipe4.domain.principal import Principal
from pipe4.exceptions import NotFound
router=APIRouter(prefix='/pipe4',tags=['Pipe 4 acquisition'],responses=STANDARD_ERRORS)
@router.post('/state-requests',status_code=status.HTTP_202_ACCEPTED,summary='Request current state',response_model=ApiSuccess[StateRequest],dependencies=[Depends(usage_guard('state_request'))])
async def create_request(request: Request,body: StateRequestBody,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.resolution.request(principal,identity=body.identity.domain(),decision_context=body.decision_context,reason=GapReason.MISSING))
@router.get('/state-requests/{request_id}',summary='Get state request',response_model=ApiSuccess[StateRequest])
async def get_request(request: Request,request_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    result=await request.app.state.container.resolution.get_request(request_id)
    if not result: raise NotFound('state request not found')
    return success(request,result)
@router.post('/revalidate',status_code=status.HTTP_202_ACCEPTED,summary='Revalidate exact current-state identity',response_model=ApiSuccess[StateRequest])
async def revalidate(request: Request,body: RevalidateRequest,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.resolution.request(principal,identity=body.identity.domain(),decision_context=body.decision_context,reason=GapReason.EXPLICIT_REVALIDATION))
@router.post('/refresh-requests',status_code=status.HTTP_202_ACCEPTED,summary='Request refresh',response_model=ApiSuccess[StateRequest])
async def refresh(request: Request,body: StateRequestBody,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.resolution.request(principal,identity=body.identity.domain(),decision_context=body.decision_context,reason=GapReason.STALE))
