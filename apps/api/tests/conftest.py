from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import pytest_asyncio

from pipe4.config import Settings
from pipe4.container import build_memory_container
from pipe4.domain.entities.models import ReferenceEntity
from pipe4.domain.evidence.models import SourceProfile
from pipe4.domain.principal import Principal


@pytest.fixture
def policy_path() -> Path:
    return Path(__file__).resolve().parents[3] / 'config' / 'policies' / 'pipe4-policy.v1.yaml'


@pytest_asyncio.fixture
async def container(policy_path: Path, tmp_path: Path):
    settings=Settings(policy_path=policy_path,evidence_local_root=tmp_path/'evidence',enable_dev_fixtures=True,jwt_hs256_secret='test-secret',internal_api_token='test-internal-token')
    c=build_memory_container(settings=settings)
    await c.repositories.save_entity(ReferenceEntity(entity_id='entity-1',entity_type='service',display_name='Main Service',latitude=6.45,longitude=3.40,aliases=['station service'],created_at=datetime.now(timezone.utc)))
    await c.sources.save_source(SourceProfile(source_id='owner-source',source_type='owner',authority_scopes={'AVAILABLE','ACCESSIBLE','WORKING','CHANGED'},reliability=0.88,evidence_capability=0.82))
    await c.sources.save_source(SourceProfile(source_id='fixture-source',source_type='institutional_api',authority_scopes={'AVAILABLE','ACCESSIBLE','WORKING','TIME','CHANGED'},reliability=0.96,evidence_capability=0.95,provider_key='fixture'))
    return c


@pytest.fixture
def admin() -> Principal:
    return Principal(subject='admin',roles=frozenset({'uwaci_internal','owner','verifier'}),permissions=frozenset({'*'}),service=True)


@pytest.fixture
def user() -> Principal:
    return Principal(subject='user-1')


@pytest.fixture
def now() -> datetime:
    return datetime.now(timezone.utc)
