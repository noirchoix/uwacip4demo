# ADR 0008 — Openapi Contract

**Status:** Accepted for reference service v1.0

## Decision

FastAPI OpenAPI is the public contract authority. Web/mobile clients mirror or generate types against committed OpenAPI.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
