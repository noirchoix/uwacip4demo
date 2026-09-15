# Ernest — Persistence, Migrations & CI

## Production destination paths

```text
app/modules/current_state/models/
app/modules/current_state/repositories/
migrations/versions/
tests/integration/current_state/
```

## Primary tasks

- implement async SQLAlchemy repository;
- generate/review Alembic migration from latest real `dev` head;
- state-version append + current projection atomic replacement;
- many-to-many state-version/observation links;
- idempotency and concurrency protections;
- indexes for current/history/entity/watch queries;
- confirm target Postgres/PostGIS capability before geospatial type decisions;
- CI/migration sanity.

## Hard rules

- repository does not commit; request session owns commit/rollback;
- no direct writes across owner-module tables;
- do not introduce outbox/Redis/Celery infrastructure without a reviewed host requirement;
- do not invent migration ancestry from this starter.

## Required proof

- repository tests against disposable test DB;
- duplicate idempotency key behaves deterministically;
- simultaneous publication cannot corrupt current pointer;
- migration upgrade/downgrade SQL reviewed;
- query plans/index intent documented for Nearby when implementation is chosen.

## Shared persistence contract

Implement `CurrentStateRepository.publish_state_version()` as one transaction with an expected-current
version check; do not reintroduce separate append/projection service calls. Observation idempotency is scoped
by `(actor_user_id, operation, key)` and must replay the same request hash while rejecting conflicting reuse.
Prove both semantics with disposable-Postgres tests before merge.
