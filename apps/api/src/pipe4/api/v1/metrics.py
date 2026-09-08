from fastapi import APIRouter, Response
from pipe4.observability.metrics import render_metrics
router=APIRouter(tags=['operations'])
@router.get('/metrics',include_in_schema=False)
async def metrics() -> Response:
    payload,content_type=render_metrics();return Response(content=payload,media_type=content_type)
