from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.usage import usage_guard
from pipe4.api.schemas import EntityResolveRequest, ProvisionalEntityRequest
from pipe4.domain.entities.models import EntityResolutionResult, ReferenceEntity
from pipe4.domain.principal import Principal
router=APIRouter(prefix='/pipe4/entities',tags=['Pipe 4 entity resolution'],responses=STANDARD_ERRORS)
@router.post('/resolve',response_model=ApiSuccess[EntityResolutionResult])
async def resolve(request: Request,body: EntityResolveRequest,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.entity_resolution.resolve(text=body.text,latitude=body.latitude,longitude=body.longitude,radius_m=body.radius_m))
@router.post('/provisional',status_code=status.HTTP_201_CREATED,response_model=ApiSuccess[ReferenceEntity],dependencies=[Depends(usage_guard('provisional_entity'))])
async def provisional(request: Request,body: ProvisionalEntityRequest,principal: Annotated[Principal,Depends(current_principal)]): return success(request,await request.app.state.container.entity_resolution.provisional(entity_type=body.entity_type,display_name=body.display_name,latitude=body.latitude,longitude=body.longitude))
