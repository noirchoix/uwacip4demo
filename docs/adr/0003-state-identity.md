# ADR 0003 — State Identity

**Status:** Accepted for reference service v1.0

## Decision

Canonical state identity is entity + object + state type + location when truth-defining + approved qualifiers. Requester/decision context do not change truth identity.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
