from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.schemas import TargetedOfferRequest
from pipe4.application.targeted_acquisition import TargetedAcquisitionView
from pipe4.domain.principal import Principal

router=APIRouter(prefix='/pipe4/acquisition-requests',tags=['Pipe 4 targeted acquisition'],responses=STANDARD_ERRORS)

@router.post('',status_code=status.HTTP_201_CREATED,response_model=ApiSuccess[TargetedAcquisitionView])
async def offer(request: Request,body: TargetedOfferRequest,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.targeted.offer_view(state_request_id=body.state_request_id,target_subject=body.target_subject,ttl_seconds=body.ttl_seconds,reward_label=body.reward_label))

@router.get('',response_model=ApiSuccess[list[TargetedAcquisitionView]])
async def list_requests(request: Request,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.targeted.list_views(principal))

@router.get('/{request_id}',response_model=ApiSuccess[TargetedAcquisitionView])
async def get_one(request: Request,request_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.targeted.get_view(principal,request_id))

@router.post('/{request_id}/accept',response_model=ApiSuccess[TargetedAcquisitionView])
async def accept(request: Request,request_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.targeted.respond_view(principal,request_id,accept=True))

@router.post('/{request_id}/decline',response_model=ApiSuccess[TargetedAcquisitionView])
async def decline(request: Request,request_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.targeted.respond_view(principal,request_id,accept=False))
