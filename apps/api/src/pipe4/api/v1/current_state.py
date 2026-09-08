from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query, Request
from pipe4.api.auth import current_principal
from pipe4.api.dependencies import state_identity
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.domain.principal import Principal
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.models import CurrentStatePresentation, StateHistoryEntry
router=APIRouter(prefix='/pipe4',tags=['Pipe 4 current state'],responses=STANDARD_ERRORS)
DecisionContextName=Literal['consumer_discovery','operational_coordination','consequential_action']
@router.get('/current',summary='Get current state',response_model=ApiSuccess[CurrentStatePresentation])
async def current(request: Request,principal: Annotated[Principal,Depends(current_principal)],identity: Annotated[StateIdentity,Depends(state_identity)],decision_context: Annotated[DecisionContextName,Query()]='consumer_discovery'):
    return success(request,await request.app.state.container.current_state.get(principal,identity=identity,decision_context=decision_context))
@router.get('/history',summary='Get safe state history',response_model=ApiSuccess[list[StateHistoryEntry]])
async def history(request: Request,principal: Annotated[Principal,Depends(current_principal)],identity: Annotated[StateIdentity,Depends(state_identity)],limit: Annotated[int,Query(ge=1,le=100)]=50):
    return success(request,await request.app.state.container.current_state.history(principal,identity=identity,limit=limit))
