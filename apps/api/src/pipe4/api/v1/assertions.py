from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.schemas import DeclarationRequest, ObservationRequest
from pipe4.domain.observation.models import ObservationRecord
from pipe4.domain.principal import Principal
from pipe4.domain.state.models import CurrentStatePresentation
router=APIRouter(prefix='/pipe4',tags=['Pipe 4 evidence'],responses=STANDARD_ERRORS)
@router.post('/declarations',status_code=status.HTTP_201_CREATED,summary='Declare current state',response_model=ApiSuccess[CurrentStatePresentation])
async def declare(request: Request,body: DeclarationRequest,principal: Annotated[Principal,Depends(current_principal)]):
    c=request.app.state.container;state=await c.declarations.declare(principal,identity=body.identity.domain(),value=body.value,observed_at=body.observed_at,source_id=body.source_id,visibility=body.visibility,permission_tags=body.permission_tags,idempotency_key=body.idempotency_key);return success(request,await c.presentation.state(principal,state))
@router.post('/observations',status_code=status.HTTP_202_ACCEPTED,summary='Submit structured observation',response_model=ApiSuccess[ObservationRecord])
async def observe(request: Request,body: ObservationRequest,principal: Annotated[Principal,Depends(current_principal)]):
    c=request.app.state.container;obs=await c.observations.submit(principal,identity=body.identity.domain(),value=body.value,observed_at=body.observed_at,source_id=body.source_id,latitude=body.latitude,longitude=body.longitude,location_accuracy_m=body.location_accuracy_m,location_description=body.location_description);return success(request,obs)
