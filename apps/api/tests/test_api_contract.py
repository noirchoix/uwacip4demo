from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from pipe4.app import create_app


@pytest.mark.asyncio
async def test_health_and_openapi_contract(container):
    app=create_app(container)
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        live=await client.get('/api/v1/health/live')
        assert live.status_code==200 and live.json()['success'] is True
        schema=(await client.get('/openapi.json')).json()
        paths=schema['paths']
        required={
            '/api/v1/pipe4/current',
            '/api/v1/pipe4/nearby',
            '/api/v1/pipe4/access-requests',
            '/api/v1/pipe4/watches',
            '/api/v1/pipe4/witness/interpret',
            '/api/v1/pipe4/witness/reports',
            '/api/v1/pipe4/entities/resolve',
            '/api/v1/pipe4/acquisition-requests',
        }
        assert required <= set(paths)


@pytest.mark.asyncio
async def test_declare_then_get_through_public_contract(container,admin):
    app=create_app(container);app.state.principal_override=admin
    body={
        'identity':{'entity_id':'entity-1','object_key':'main','state_type':'AVAILABLE','qualifiers':{}},
        'value':{'kind':'boolean','value':True},
        'observed_at':datetime.now(timezone.utc).isoformat(),
        'source_id':'owner-source',
        'visibility':'PUBLIC',
        'permission_tags':[],
        'idempotency_key':'api-test',
    }
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        created=await client.post('/api/v1/pipe4/declarations',json=body)
        assert created.status_code==201,created.text
        current=await client.get('/api/v1/pipe4/current',params={'entity_id':'entity-1','state_type':'AVAILABLE','object_key':'main'})
        assert current.status_code==200
        payload=current.json();assert payload['success'] is True and payload['data']['value']['value'] is True


@pytest.mark.asyncio
async def test_validation_errors_use_standard_envelope(container,admin):
    app=create_app(container);app.state.principal_override=admin
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        response=await client.get('/api/v1/pipe4/current',params={'entity_id':'entity-1','state_type':'NOT_A_STATE'})
        assert response.status_code==422 and response.json()['error']['code']=='VALIDATION_ERROR'
