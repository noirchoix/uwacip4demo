from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from pydantic import BaseModel, ConfigDict
from pipe4.api.auth import current_principal
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
from pipe4.api.usage import usage_guard
from pipe4.api.schemas import WitnessInterpretRequest, WitnessReportReceipt, WitnessReportRequest
from pipe4.application.witness import WitnessInterpretationResult
from pipe4.domain.observation.models import ObservationRecord
from pipe4.domain.principal import Principal

class AudioReportReceipt(BaseModel):
    model_config=ConfigDict(extra='forbid')
    status: str
    audio_ref: str
    interpretation: WitnessInterpretationResult | None=None
    observation: ObservationRecord | None=None
    message: str | None=None

router=APIRouter(prefix='/pipe4/witness',tags=['Pipe 4 witness reporting'],responses=STANDARD_ERRORS)

@router.post('/interpret',response_model=ApiSuccess[WitnessInterpretationResult],dependencies=[Depends(usage_guard('witness_interpret'))])
async def interpret(request: Request,body: WitnessInterpretRequest,principal: Annotated[Principal,Depends(current_principal)]):
    return success(request,await request.app.state.container.witness.interpret(text=body.text,latitude=body.latitude,longitude=body.longitude))

@router.post('/reports',status_code=status.HTTP_202_ACCEPTED,response_model=ApiSuccess[WitnessReportReceipt],dependencies=[Depends(usage_guard('witness_report'))])
async def report(request: Request,body: WitnessReportRequest,principal: Annotated[Principal,Depends(current_principal)]):
    interpretation,observation=await request.app.state.container.witness.report(principal,text=body.text,observed_at=body.observed_at,entity_id=body.entity_id,object_key=body.object_key,state_type=body.state_type,value=body.value,latitude=body.latitude,longitude=body.longitude,location_accuracy_m=body.location_accuracy_m,location_description=body.location_description)
    if observation and body.targeted_request_id:
        await request.app.state.container.targeted.complete(principal,body.targeted_request_id,observation_id=observation.observation_id)
    return success(request,WitnessReportReceipt(interpretation=interpretation,observation=observation,you_reported=body.text,uwaci_status='VERIFYING' if observation else 'NEEDS_CLARIFICATION'))

@router.post('/audio-reports',status_code=status.HTTP_202_ACCEPTED,response_model=ApiSuccess[AudioReportReceipt],dependencies=[Depends(usage_guard('witness_audio'))])
async def audio_report(request: Request,principal: Annotated[Principal,Depends(current_principal)],audio: UploadFile=File(...),transcript: str | None=Form(default=None),observed_at: str=Form(...),entity_id: str | None=Form(default=None),targeted_request_id: str | None=Form(default=None),latitude: float | None=Form(default=None),longitude: float | None=Form(default=None)):
    from datetime import datetime
    data=await audio.read();stored=await request.app.state.container.witness.store_audio(data=data,content_type=audio.content_type or 'application/octet-stream',file_name=audio.filename or 'report.audio')
    if not transcript:
        return success(request,AudioReportReceipt(status='PROCESSING',audio_ref=stored.object_ref,message='Audio was stored durably. Configure the AI/STT gateway or submit a transcript to complete interpretation.'))
    interpretation,observation=await request.app.state.container.witness.report(principal,text=transcript,observed_at=datetime.fromisoformat(observed_at.replace('Z','+00:00')),entity_id=entity_id,latitude=latitude,longitude=longitude)
    if observation and targeted_request_id:
        await request.app.state.container.targeted.complete(principal,targeted_request_id,observation_id=observation.observation_id)
    return success(request,AudioReportReceipt(status='VERIFYING' if observation else 'NEEDS_CLARIFICATION',audio_ref=stored.object_ref,interpretation=interpretation,observation=observation))
