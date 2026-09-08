from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from pipe4.api.envelope import ApiSuccess, STANDARD_ERRORS
from pipe4.api.responses import success
router=APIRouter(tags=['health'],responses=STANDARD_ERRORS)
@router.get('/health/live',summary='Process liveness',response_model=ApiSuccess[dict[str,str]])
async def live(request: Request): return success(request,{'status':'ok'})
@router.get('/health/ready',summary='Dependency readiness',response_model=ApiSuccess[dict[str,object]])
async def ready(request: Request):
    container=request.app.state.container; result={'database':'unknown','redis':'unknown'}
    engine=getattr(container,'engine',None)
    if engine is None: result['database']='memory'
    else:
        async with engine.connect() as conn:
            tables=await conn.execute(text("SELECT to_regclass('public.state_version'), to_regclass('public.outbox')"))
            state_table,outbox_table=tables.one()
            if state_table is None or outbox_table is None:
                raise HTTPException(status_code=503,detail='database schema is not ready')
            result['database']='ok'
    redis=getattr(container,'redis',None)
    if redis is None: result['redis']='not_required'
    else: result['redis']='ok' if await redis.ping() else 'failed'
    return success(request,{'status':'ready','dependencies':result})
