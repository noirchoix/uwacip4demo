# ADR 0007 — Policy Versioning

**Status:** Accepted for reference service v1.0

## Decision

Freshness, confidence, verification, ranking, source learning and nearby ranking are validated versioned policy, not scattered magic constants.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
