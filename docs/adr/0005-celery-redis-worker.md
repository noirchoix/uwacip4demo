# ADR 0005 — Celery Redis Worker

**Status:** Accepted for reference service v1.0

## Decision

Use Celery + Redis for standalone slow/retryable acquisition, verification, expiry, and outbox work. Host integration may replace this through JobSchedulerPort.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
