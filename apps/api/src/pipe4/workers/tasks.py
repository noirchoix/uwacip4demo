from __future__ import annotations
import asyncio, logging
from pipe4.config import get_settings
from pipe4.container import build_production_container
from pipe4.domain.state.enums import PublishedStateLifecycle
from pipe4.workers.celery_app import celery_app
logger=logging.getLogger(__name__)

def run(coro): return asyncio.run(coro)

async def with_container(fn):
    container=await build_production_container(get_settings())
    try: return await fn(container)
    finally: await container.close()

@celery_app.task(name='pipe4.acquire',bind=True,autoretry_for=(Exception,),retry_backoff=True,retry_jitter=True,max_retries=3)
def acquire(self,job_id: str): return run(with_container(lambda c:c.acquisition.run_job(job_id)))

@celery_app.task(name='pipe4.verify_observation',bind=True,autoretry_for=(Exception,),retry_backoff=True,retry_jitter=True,max_retries=3)
def verify_observation(self,observation_id: str): return run(with_container(lambda c:c.verification.verify_observation(observation_id)))

@celery_app.task(name='pipe4.evaluate_watches',bind=True,autoretry_for=(Exception,),retry_backoff=True,retry_jitter=True,max_retries=3)
def evaluate_watches(self,state_version_id: str):
    async def work(c):
        state=await c.repositories.get_version(state_version_id); return await c.watches.evaluate(state) if state else 0
    return run(with_container(work))

@celery_app.task(name='pipe4.dispatch_outbox')
def dispatch_outbox():
    async def work(c):
        if c.event_publisher is None: return 0
        rows=await c.repositories.pending_outbox(limit=100);count=0
        for row in rows:
            try: await c.event_publisher.publish(row.event);await c.repositories.mark_outbox_published(row.outbox_id,published_at=c.publication.clock.now());count+=1
            except Exception as exc: await c.repositories.mark_outbox_failed(row.outbox_id,error=str(exc))
        return count
    return run(with_container(work))

@celery_app.task(name='pipe4.expire_states')
def expire_states():
    async def work(c):
        now=c.publication.clock.now();count=0
        for state in await c.repositories.list_current():
            if state.expires_at and state.expires_at<=now and state.lifecycle_status not in {PublishedStateLifecycle.EXPIRED,PublishedStateLifecycle.REPLACED}:
                await c.publication.expire(state.state_version_id);count+=1
        return count
    return run(with_container(work))
