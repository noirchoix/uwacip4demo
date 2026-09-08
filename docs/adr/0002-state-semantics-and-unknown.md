# ADR 0002 — State Semantics And Unknown

**Status:** Accepted for reference service v1.0

## Decision

Separate request, observation, epistemic, verification, and published-state lifecycles. UNKNOWN is a knowledge outcome, not a fabricated StateVersion.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
