from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response, status
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.schemas import WatchCreateRequest
from pipe4.application.watches import WatchView
from pipe4.domain.principal import Principal

router=APIRouter(prefix='/pipe4/watches',tags=['Pipe 4 watches'],responses=STANDARD_ERRORS)

@router.post('',status_code=status.HTTP_201_CREATED,response_model=ApiSuccess[WatchView])
async def create(request: Request,body: WatchCreateRequest,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.watches.create_view(principal,body.condition))

@router.get('',response_model=ApiSuccess[list[WatchView]])
async def list_watches(request: Request,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.watches.list_views(principal))

@router.get('/{watch_id}',response_model=ApiSuccess[WatchView])
async def get_watch(request: Request,watch_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.watches.get_view(principal,watch_id))

@router.delete('/{watch_id}',status_code=status.HTTP_204_NO_CONTENT,response_class=Response)
async def remove(request: Request,watch_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    await request.app.state.container.watches.remove(principal,watch_id);return Response(status_code=204)

@router.post('/{watch_id}/pause',response_model=ApiSuccess[WatchView])
async def pause(request: Request,watch_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.watches.set_paused_view(principal,watch_id,paused=True))

@router.post('/{watch_id}/resume',response_model=ApiSuccess[WatchView])
async def resume(request: Request,watch_id: str,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.watches.set_paused_view(principal,watch_id,paused=False))
