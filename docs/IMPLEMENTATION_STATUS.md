# Pipe 4 Implementation Status

This document states what is executable in the starter and what must still be implemented in the real UWACI backend. It is intentionally conservative: scaffolded integration is not counted as completed functionality.

## Executable reference behavior

The starter contains production-shaped code and deterministic tests for:

- the exact five current-state types;
- canonical `StateIdentity` and qualifier ordering;
- typed state values and validation;
- observation, state, access, and WATCH lifecycle guards;
- immutable/versioned state records;
- nullable confidence and expiry contracts;
- conservative publication policy;
- UNKNOWN / DISPUTED / STALE / INFERRED presentation mapping;
- typed WATCH operators and deterministic canonicalization;
- typed access scopes and non-broadening approval;
- principal-scoped idempotency semantics and request hashes;
- deterministic Nearby relevance through `NearbyRankingPolicy`;
- mobile-facing Pydantic contracts;
- SQLAlchemy model skeletons using host conventions;
- ports for Knowledge, Core AI, Notification, entity/location boundaries, and Pipe-4-owned persistence.

## Integration work still required

The following must be completed against the current `uwaci-backend` `dev` branch:

| Area | Required implementation | Primary owner |
|---|---|---|
| API | FastAPI handlers, dependency wiring, route registration | Victory + Jacob |
| Persistence | async repository, atomic publication, live Alembic revision, concurrency tests | Ernest + Ibrahim |
| Knowledge | provenance-per-observation adapter | Victory + Ernest |
| Core AI | witness interpretation and approved transcription boundary | Victory |
| Notification | safe WATCH/access/acquisition event integration | Victory + RoboTech |
| Identity/auth | server-side principal and authorization integration | Victory + Jacob |
| Locator/Presence | canonical owner-module adapters when available | Samuel + Victory |
| Nearby | repository query strategy and geo capability decision | RoboTech + Ernest |
| WATCH | trigger orchestration, permission re-check, notification flow | RoboTech + Victory |
| Acquisition | targeted acquisition orchestration | Victory + RoboTech |
| Acceptance | end-to-end closure of tracked acceptance gates | Jacob + owners |

## Current environment decisions

- Pipe 4 is `app/modules/current_state` inside the FastAPI modular monolith.
- Public routes remain `/api/v1/pipe4/...`.
- Use the backend's current in-process domain-event mechanism unless a reviewed scale requirement justifies more infrastructure.
- Nearby stays behind a repository abstraction; confirm target database/PostGIS capability before adding a hard geospatial dependency.
- Knowledge owns generic provenance semantics; provenance attaches to observations and state versions link to one or more observations.
- Mobile consumes privacy-safe read models and does not become a canonical source of truth.

## Merge gates

A feature is not complete until the relevant domain, persistence, contract, owner-module, security, and acceptance behavior is proven by executable tests. See:

- `docs/TESTING_STANDARD.md`
- `docs/SECURITY_TEST_MATRIX.md`
- `docs/ACCEPTANCE_TRACEABILITY.md`
- `docs/PR_CHECKLIST.md`
