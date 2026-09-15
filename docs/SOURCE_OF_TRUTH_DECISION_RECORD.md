# Pipe 4 Source-of-Truth Decision Record

**Status:** Accepted engineering baseline
**Decision authority:** Samuel / backend integration review

## Source precedence

When artifacts disagree, use this order and escalate material conflicts:

1. **Approved Pipe 4 requirements and acceptance intent** — product/domain behavior.
2. **Current `uwaci-backend` `dev` branch** — host architecture, ownership, infrastructure, database, API envelope, auth, and CI conventions.
3. **Current `uwaci-mobile` contract** — consumer-visible request/response expectations coordinated with backend truth and security semantics.
4. **This starter** — implementation accelerator, reference behavior, and team coordination.
5. **Testing/engineering resources** — development method and quality guidance.

No lower source silently overrides a higher one.

## Accepted implementation decisions

### DR-01 — Host location

Pipe 4 is implemented as `app/modules/current_state` inside the existing FastAPI modular monolith.

### DR-02 — Public namespace

Mobile-facing routes remain under `/api/v1/pipe4/...` even though the backend module is named `current_state`.

### DR-03 — Canonical truth is server-side

Clients submit observations and consume read models. They do not author canonical current state.

### DR-04 — Observation is not publication

A witness report creates evidence first. Publication of a `StateVersion` requires resolution policy. Reporter receipts must not imply that UWACI has accepted the claim as current truth.

### DR-05 — History is append-preserving

Published state is versioned. A new accepted truth appends a `StateVersion`; the current projection may move atomically to the new version. Existing versions are not rewritten.

### DR-06 — Knowledge owns provenance semantics

Pipe 4 does not create a parallel generic provenance/trust system. Provenance attaches to Pipe 4 observations; state versions may link to multiple observations.

### DR-07 — Confidence is not fabricated

Source confidence remains optional source context. Pipe 4 does not reinterpret it as a calibrated probability of truth. Public confidence remains nullable until an explicitly approved model exists.

### DR-08 — AI is assistive

AI may transcribe, extract, summarize, or structure evidence through the approved Core AI boundary. Model output alone is not canonical evidence or truth.

### DR-09 — Owner modules retain ownership

Identity owns authenticated actors and authorization primitives; Knowledge owns generic provenance/verification support; Notification owns delivery; Core AI owns provider composition; Locator and Presence remain canonical boundaries when available.

### DR-10 — Infrastructure follows demonstrated need

Use the backend's existing in-process domain-event mechanism for the current increment. Redis, Celery, transactional outbox, PostGIS, or other infrastructure requires a reviewed need rather than convenience.

### DR-11 — Geospatial details stay behind repositories

Nearby business logic must not depend directly on a specific geospatial database implementation. Confirm target environment capability before selecting concrete spatial types/queries.

### DR-12 — WATCH is typed and canonicalized

WATCH uses the approved operator vocabulary and JSON-safe scalar targets. Equivalent subscriptions canonicalize to the same underlying work key.

### DR-13 — Access is typed and least-privilege

Current-state access uses explicit read permission and typed `AccessScope`. Approval may narrow requested scope but may not broaden it.

### DR-14 — Publication is atomic

Appending the state version and moving the current projection are one repository transaction with expected-current concurrency protection.

### DR-15 — Idempotency is principal-scoped

Observation retries use `(actor_user_id, operation, idempotency_key)` plus a canonical request hash. Reuse with different payload must be rejected.

### DR-16 — Nearby ranking policy is explicit

`NearbyRankingPolicy` owns relevance weights. Ranking is deterministic, explainable, configurable, and separate from epistemic confidence.

### DR-17 — Internal record style follows host conventions

Use frozen/slotted dataclasses for simple immutable internal records where practical; use Pydantic for external schemas and validation-heavy value objects.

## Decisions requiring live environment evidence

- exact PostGIS availability and concrete Nearby SQL strategy;
- final Locator/Presence owner-module APIs where not yet available;
- final Core AI transcription boundary for witness audio;
- exact Alembic parent revision on the implementation branch;
- whether future scale requires worker/outbox infrastructure;
- any future calibrated confidence/truth model.

Open decisions are escalation points, not permission to create parallel ownership.
