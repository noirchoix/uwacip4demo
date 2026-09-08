from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, ConfigDict
from pipe4.api.auth import internal_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.schemas import SourceCreateRequest, SourceOutcomeRequest, VerificationRequest
from pipe4.domain.evidence.models import SourceProfile
from pipe4.domain.events.models import DomainEvent
from pipe4.domain.principal import Principal
from pipe4.domain.state.models import StateVersion

class PolicyInspection(BaseModel):
    model_config=ConfigDict(extra='forbid')
    version: str
    content_hash: str
    state_types: list[str]
    decision_contexts: list[str]
    nearby_weights: dict[str,float]

router=APIRouter(prefix='/internal/pipe4',tags=['Pipe 4 internal'],responses=STANDARD_ERRORS)
@router.post('/verifications',response_model=ApiSuccess[StateVersion | None])
async def verify(request: Request,body: VerificationRequest,principal: Annotated[Principal,Depends(internal_principal)]): return success(request,await request.app.state.container.verification.verify_observation(body.observation_id))
@router.post('/state-versions/{state_version_id}/expire',response_model=ApiSuccess[StateVersion])
async def expire(request: Request,state_version_id: str,principal: Annotated[Principal,Depends(internal_principal)]): return success(request,await request.app.state.container.publication.expire(state_version_id))
@router.post('/source-outcomes',response_model=ApiSuccess[SourceProfile])
async def source_outcome(request: Request,body: SourceOutcomeRequest,principal: Annotated[Principal,Depends(internal_principal)]): return success(request,await request.app.state.container.sources.record_outcome(body.source_id,entity_id=body.entity_id,state_type=body.state_type,correct=body.correct))
@router.post('/sources',status_code=status.HTTP_201_CREATED,response_model=ApiSuccess[SourceProfile])
async def source_create(request: Request,body: SourceCreateRequest,principal: Annotated[Principal,Depends(internal_principal)]):
    source=SourceProfile.model_validate(body.model_dump());await request.app.state.container.sources.save_source(source);return success(request,source)
@router.get('/events',response_model=ApiSuccess[list[DomainEvent]])
async def events(request: Request,principal: Annotated[Principal,Depends(internal_principal)]): return success(request,await request.app.state.container.repositories.list_events())
@router.get('/policies',response_model=ApiSuccess[PolicyInspection])
async def policies(request: Request,principal: Annotated[Principal,Depends(internal_principal)]):
    bundle=request.app.state.container.policies.bundle
    return success(request,PolicyInspection(version=bundle.version,content_hash=bundle.content_hash,state_types=[item.value for item in bundle.state_types],decision_contexts=list(bundle.decision_contexts),nearby_weights=bundle.nearby_ranking.weights))
