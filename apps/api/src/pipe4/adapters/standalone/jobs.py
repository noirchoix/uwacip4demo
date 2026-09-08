from __future__ import annotations


class InlineJobScheduler:
    """Test/dev scheduler that records work without hiding business logic in dependencies."""
    def __init__(self) -> None:
        self.acquisition_jobs: list[str]=[]; self.verification_jobs: list[str]=[]; self.watch_jobs: list[str]=[]; self.outbox_requests=0
    async def enqueue_acquisition(self, job_id: str) -> None: self.acquisition_jobs.append(job_id)
    async def enqueue_verification(self, observation_id: str) -> None: self.verification_jobs.append(observation_id)
    async def enqueue_watch_evaluation(self, state_version_id: str) -> None: self.watch_jobs.append(state_version_id)
    async def enqueue_outbox_dispatch(self) -> None: self.outbox_requests += 1
