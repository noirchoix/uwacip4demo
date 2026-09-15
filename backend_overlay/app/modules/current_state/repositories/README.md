# Repository implementation workstream

`CurrentStateRepository` is defined under `ports/repository.py`.

Ernest should implement `SQLAlchemyCurrentStateRepository` in this directory after syncing the actual migration head.

Important implementation requirements:

- use the request-scoped `AsyncSession` from `get_db_session`;
- never commit inside the repository; session lifecycle belongs to the platform dependency;
- append state versions;
- update `current_state_current_projection` atomically;
- use row-level locking or an equivalent deterministic concurrency mechanism during publication;
- enforce idempotency for witness intake;
- batch queries; avoid N+1;
- use explicit limits and stable ordering;
- do not query/write Knowledge/Identity/Notification private tables directly.
