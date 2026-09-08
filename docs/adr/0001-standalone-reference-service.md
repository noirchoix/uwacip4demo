# ADR 0001 — Standalone Reference Service

**Status:** Accepted for reference service v1.0

## Decision

Use one independently deployable Pipe 4 service with ports/adapters so the same domain semantics can integrate into UWACI without a second business-logic implementation.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
