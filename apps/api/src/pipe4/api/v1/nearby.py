from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.usage import usage_guard
from pipe4.application.nearby import NearbyResult
from pipe4.domain.principal import Principal
router=APIRouter(prefix='/pipe4',tags=['Pipe 4 nearby'],responses=STANDARD_ERRORS)
@router.get('/nearby',response_model=ApiSuccess[list[NearbyResult]],dependencies=[Depends(usage_guard('nearby'))])
async def nearby(request: Request,principal: Annotated[Principal,Depends(current_principal)],latitude: Annotated[float,Query(ge=-90,le=90)],longitude: Annotated[float,Query(ge=-180,le=180)],radius_m: Annotated[int,Query(gt=0,le=50000)]=5000,urgency: Annotated[float,Query(ge=0,le=1)]=0.5,uncertainty_consequence: Annotated[float,Query(ge=0,le=1)]=0.25,intent_relevance: Annotated[float,Query(ge=0,le=1)]=0.5): return success(request,await request.app.state.container.nearby.search(principal,latitude=latitude,longitude=longitude,radius_m=radius_m,urgency=urgency,uncertainty_consequence=uncertainty_consequence,intent_relevance=intent_relevance))
