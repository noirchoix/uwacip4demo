from __future__ import annotations

import asyncio


class CeleryJobScheduler:
    def __init__(self, celery_app) -> None: self.celery_app=celery_app
    async def _send(self, name: str, args: list[str] | None=None) -> None:
        await asyncio.to_thread(self.celery_app.send_task,name,args=args or [])
    async def enqueue_acquisition(self, job_id: str) -> None: await self._send('pipe4.acquire',[job_id])
    async def enqueue_verification(self, observation_id: str) -> None: await self._send('pipe4.verify_observation',[observation_id])
    async def enqueue_watch_evaluation(self, state_version_id: str) -> None: await self._send('pipe4.evaluate_watches',[state_version_id])
    async def enqueue_outbox_dispatch(self) -> None: await self._send('pipe4.dispatch_outbox')
