from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.schemas import AccessCreateRequest, AccessDecisionRequest
from pipe4.domain.access.models import AccessRequest
from pipe4.domain.principal import Principal
from pipe4.exceptions import NotFound, PermissionDenied
router=APIRouter(prefix='/pipe4/access-requests',tags=['Pipe 4 access'],responses=STANDARD_ERRORS)
@router.post('',status_code=status.HTTP_201_CREATED,response_model=ApiSuccess[AccessRequest])
async def create(request: Request,body: AccessCreateRequest,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.access.request(principal,entity_id=body.entity_id,identity_key=body.identity_key,permission=body.permission,scope=body.scope))
@router.get('',response_model=ApiSuccess[list[AccessRequest]])
async def list_requests(request: Request,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.access.list(principal))
@router.get('/{request_id}',response_model=ApiSuccess[AccessRequest])
async def get_one(request: Request,request_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    result=await request.app.state.container.repositories.get_access_request(request_id)
    if not result: raise NotFound('access request not found')
    if result.requester_subject!=principal.subject and not await request.app.state.container.authorization.can_decide_access(principal,entity_id=result.target_entity_id): raise PermissionDenied('access request is not visible to this subject')
    return success(request,result)
@router.post('/{request_id}/approve',response_model=ApiSuccess[AccessRequest])
async def approve(request: Request,request_id: str,body: AccessDecisionRequest,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.access.decide(principal,request_id,approve=True,reason=body.reason,expires_at=body.expires_at))
@router.post('/{request_id}/deny',response_model=ApiSuccess[AccessRequest])
async def deny(request: Request,request_id: str,body: AccessDecisionRequest,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.access.decide(principal,request_id,approve=False,reason=body.reason))
@router.post('/{request_id}/revoke',response_model=ApiSuccess[AccessRequest])
async def revoke(request: Request,request_id: str,body: AccessDecisionRequest,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.access.revoke(principal,request_id,reason=body.reason))
@router.post('/{request_id}/cancel',response_model=ApiSuccess[AccessRequest])
async def cancel(request: Request,request_id: str,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.access.cancel(principal,request_id))
