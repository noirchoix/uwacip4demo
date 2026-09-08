from __future__ import annotations

import uuid
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from pipe4.api.envelope import ApiErrorBody, ApiFailure, ApiMeta
from pipe4.api.v1 import access, assertions, current_state, disputes, entities, health, internal, metrics, nearby, requests, targeted, watches, witness
from pipe4.config import get_settings
from pipe4.container import ApplicationContainer, build_production_container
from pipe4.exceptions import Pipe4Error
from pipe4.logging import configure_logging
from pipe4.observability.metrics import record_request


def create_app(container: ApplicationContainer | None=None) -> FastAPI:
    settings=container.settings if container else get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        runtime=container or await build_production_container(settings)
        app.state.container=runtime
        try: yield
        finally:
            if container is None: await runtime.close()

    app=FastAPI(
        title='UWACI Pipe 4 Current Reality API',
        version='1.0.0',
        description='Horizontal current-reality resolution, evidence, verification, WATCH, access, nearby and acquisition service.',
        docs_url='/docs' if settings.environment!='production' else None,
        redoc_url='/redoc' if settings.environment!='production' else None,
        lifespan=lifespan,
    )
    configure_logging(settings.log_level)
    if container is not None:
        app.state.container=container
    app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=['GET','POST','DELETE','OPTIONS'],allow_headers=['Authorization','Content-Type','X-Internal-Token','X-Request-ID'])

    @app.middleware('http')
    async def request_context(request: Request, call_next):
        request.state.request_id=request.headers.get('X-Request-ID') or str(uuid.uuid4());request.state.request_timestamp=datetime.now(timezone.utc);started=time.perf_counter()
        response=await call_next(request);duration=time.perf_counter()-started;record_request(request.method,request.url.path,response.status_code,duration);response.headers['X-Request-ID']=request.state.request_id;response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='no-referrer';return response

    @app.exception_handler(Pipe4Error)
    async def pipe4_error(request: Request, exc: Pipe4Error):
        body=ApiFailure(error=ApiErrorBody(code=exc.code,message=exc.message,details=exc.details or None),meta=ApiMeta(request_id=getattr(request.state,'request_id',str(uuid.uuid4())),timestamp=datetime.now(timezone.utc)))
        return JSONResponse(status_code=exc.status_code,content=jsonable_encoder(body))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        body=ApiFailure(error=ApiErrorBody(code='VALIDATION_ERROR',message='Request validation failed.',details={'errors':exc.errors()}),meta=ApiMeta(request_id=getattr(request.state,'request_id',str(uuid.uuid4())),timestamp=datetime.now(timezone.utc)))
        return JSONResponse(status_code=422,content=jsonable_encoder(body))

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logging.getLogger(__name__).exception('unhandled request error',extra={'request_id':getattr(request.state,'request_id',None)})
        body=ApiFailure(error=ApiErrorBody(code='INTERNAL_ERROR',message='An unexpected server error occurred.'),meta=ApiMeta(request_id=getattr(request.state,'request_id',str(uuid.uuid4())),timestamp=datetime.now(timezone.utc)))
        return JSONResponse(status_code=500,content=jsonable_encoder(body))

    prefix='/api/v1'
    for router in (health.router,metrics.router,current_state.router,assertions.router,requests.router,disputes.router,nearby.router,access.router,watches.router,witness.router,entities.router,targeted.router,internal.router): app.include_router(router,prefix=prefix)
    return app

app=create_app()
