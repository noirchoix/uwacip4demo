# Pipe 4 Testing Standard

## Mandatory development cycle

Every behavior is implemented through RED → GREEN → REFACTOR.

1. write one failing test;
2. verify the failure is for the intended missing behavior;
3. implement the smallest production change;
4. run the focused test;
5. refactor only while green;
6. run neighboring tests;
7. run the full quality gate before PR.

## Test pyramid for this module

- **Unit**: domain invariants, transition rules, ranking, canonicalization, presentation mapping.
- **Repository**: SQLAlchemy persistence, atomic projection replacement, idempotency, query limits.
- **Contract**: every mobile-facing endpoint + error envelope + auth.
- **Integration**: Knowledge, Identity, Notification, Core AI adapters using fakes or disposable DB as appropriate.
- **Acceptance**: AC-01..20 and ADD-AC-01..10; edge cases tracked explicitly.

## Mocking rules

- test real behavior;
- use fakes at stable external/module boundaries;
- do not assert that a mock merely existed or was called unless the interaction itself is the contract;
- do not add test-only methods to production classes;
- understand side effects before mocking;
- mock complete data shapes, not convenient partial objects.

## Minimum PR gate

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy app tests scripts
uv run pytest
uv run alembic upgrade head --sql
```

Security/privacy tests are mandatory for:

- access decisions;
- public witness presentation;
- event payload sanitization;
- mobile DTOs;
- entity-resolution leakage;
- user ownership / authentication paths.

## Shared hardening tests

Before implementing adapters/routes, preserve tests proving:

- WATCH rejects unknown operators, arbitrary object targets and non-numeric threshold targets;
- access scopes canonicalize deterministically and approved requests require audit/grant metadata;
- state identity hashes reject malformed/non-hex values at domain and API boundaries;
- idempotency keys obey host bounds and request hashes are lowercase SHA-256;
- repository API exposes one atomic publication operation with expected-current concurrency input;
- observation idempotency uniqueness is scoped by actor + operation + key;
- Nearby weights are explicit/configurable and zero-total policies are invalid;
- record-style domain entities remain immutable and preserve validation.

Repository implementations must add real database tests for replay-vs-conflict idempotency and simultaneous
state publication. Those cannot be proven by interface/unit tests alone.
