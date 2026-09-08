# ADR 0004 — Transactional Outbox

**Status:** Accepted for reference service v1.0

## Decision

Persist consequential state mutation and domain event/outbox record atomically. Redis publication is an acceleration mechanism, not durable truth.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
