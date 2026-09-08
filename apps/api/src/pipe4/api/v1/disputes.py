from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.schemas import DisputeRequest
from pipe4.application.disputes import DisputeReceipt
from pipe4.domain.principal import Principal

router=APIRouter(prefix='/pipe4',tags=['Pipe 4 disputes'],responses=STANDARD_ERRORS)

@router.post('/disputes',status_code=status.HTTP_202_ACCEPTED,response_model=ApiSuccess[DisputeReceipt],summary='Dispute a current state')
async def dispute(request: Request,body: DisputeRequest,principal: Annotated[Principal,Depends(current_principal)]):
    result=await request.app.state.container.disputes.open(
        principal,
        identity=body.identity.domain(),
        reason=body.reason,
        proposed_value=body.proposed_value,
        observed_at=body.observed_at,
        latitude=body.latitude,
        longitude=body.longitude,
        location_accuracy_m=body.location_accuracy_m,
        location_description=body.location_description,
    )
    return success(request,result)
