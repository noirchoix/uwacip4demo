# ADR 0009 — Web Api Topology

**Status:** Accepted for reference service v1.0

## Decision

Run SvelteKit and FastAPI as separate production processes behind a reverse proxy. FastAPI does not serve the production web app.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
