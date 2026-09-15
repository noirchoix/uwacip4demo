# UWACI Pipe 4 — Backend Team Starter

This repository is the engineering baseline for implementing **Pipe 4: Current Reality & State Completion** inside the existing UWACI FastAPI backend.

It is designed for engineers joining the work with no prior project context. The repository contains:

- production-shaped `current_state` domain code and contracts;
- workstream ownership and handoff rules;
- reference and host-path tests;
- mobile/API contract information;
- migration, security, acceptance, and integration guidance;
- scripts for validating and applying the starter to a fresh `uwaci-backend` clone.

## What Pipe 4 does

Pipe 4 resolves the best-supported current state of an entity, resource, service, place, or capability across five canonical state types:

- `AVAILABLE`
- `ACCESSIBLE`
- `WORKING`
- `TIME`
- `CHANGED`

The server owns canonical current-state publication. Mobile and other clients submit observations and consume read models; they do not define truth.

Core rules:

- observation is evidence, not canonical state;
- history is append-preserving and versioned;
- uncertainty may remain `UNKNOWN`, `VERIFYING`, `DISPUTED`, `STALE`, or `INFERRED`;
- AI may interpret evidence but cannot become canonical truth;
- Identity, Knowledge, Core AI, Notification, Locator, and Presence retain their existing ownership;
- Pipe 4 owns only its current-state-specific records and workflows;
- public DTOs must be privacy-safe;
- tests are part of implementation, not a later phase.

## Repository layout

```text
backend_overlay/
  app/modules/current_state/     production destination package
  tests/unit/current_state/      host-path unit tests
  docs/implementation/           progress tracker copied into the backend

contracts/                       mobile/API contract freeze and endpoint manifest
docs/                            architecture, status, testing, security, migration, acceptance
patches/                         reviewed mobile-contract and router integration guidance
reference_tests/                 deterministic tests for the reference domain behavior
resources/testing/               team testing and review resources
scripts/                         validation, compatibility, contract, and overlay helpers
workstreams/                     ownership guides; never imported by runtime code
```

## Important architecture boundary

Production code belongs under normal UWACI backend paths such as:

```text
app/modules/current_state/
tests/unit/current_state/
tests/integration/current_state/
tests/contract/
migrations/versions/
docs/implementation/
```

`workstreams/<owner>/` exists only to coordinate responsibility. Do not import runtime code from those directories.

## Prerequisites

For the real backend:

- Git
- Python 3.12+
- `uv`
- Docker, where required by the backend database/integration environment

The inspected UWACI backend uses FastAPI, SQLAlchemy, Alembic, PostgreSQL, Ruff, strict mypy, pytest, and `uv`.

## Validate this starter

From this repository root:

```bash
python scripts/validate_starter.py
python -m pytest -q reference_tests
```

The validator checks required starter structure, the 17-route mobile manifest, runtime import boundaries, line-length rules, generated cache files, ownership metadata, and hardened shared contracts.

## Integrate into a fresh UWACI backend clone

Clone and prepare the host repository:

```bash
git clone <uwaci-backend-url>
cd uwaci-backend
git switch dev
git pull --ff-only origin dev
git switch -c feature/pipe4-<workstream>
uv sync --locked --all-groups
```

From this starter repository, check compatibility before copying anything:

```bash
python scripts/check_host_compatibility.py --repo /path/to/uwaci-backend
python scripts/apply_overlay.py --repo /path/to/uwaci-backend --dry-run
python scripts/apply_overlay.py --repo /path/to/uwaci-backend
```

The overlay helper refuses protected branches and refuses to overwrite existing files. A conflict must be reviewed rather than bypassed with a force copy.

## Run the integrated backend

The starter itself is **not a separate FastAPI application**. It supplies the `current_state` module and tests that are integrated into `uwaci-backend`.

In the backend repository, use the host application's normal runtime:

```bash
docker compose up -d db
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

Pipe 4 product routes remain under:

```text
/api/v1/pipe4/...
```

Route registration, concrete repositories, the live Alembic revision, and real owner-module adapters must be implemented against the current `dev` branch before every Pipe 4 endpoint is expected to run end to end.

## Run tests in the integrated backend

Focused current-state tests:

```bash
uv run pytest tests/unit/current_state -q
```

Full backend quality gate before PR:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy app tests scripts
uv run pytest
uv run alembic upgrade head --sql
uv run pip-audit
```

Run database-backed integration tests and Docker checks when the environment supports them.

## Development method

Every new behavior follows:

```text
RED      write one failing behavior test
VERIFY   confirm the expected failure
GREEN    implement the smallest production change
VERIFY   rerun the focused test
REFACTOR improve design without changing behavior
REGRESS  run neighboring and full gates
```

Do not weaken tests to fit implementation. Test real behavior and use fakes only at stable external/module boundaries when necessary.

## Source-of-truth order

When artifacts disagree:

1. approved Pipe 4 requirements and acceptance intent;
2. current `uwaci-backend` `dev` branch for host architecture and ownership;
3. current `uwaci-mobile` contract for consumer-visible behavior;
4. this starter for implementation patterns and team coordination;
5. testing/engineering resources for development method.

Material conflicts are escalated to Samuel rather than silently resolved in one workstream.

## Team ownership

| Area | Primary owner |
|---|---|
| Integration authority and final review | Samuel |
| Service/API composition and adapters | Victory Azundo |
| Truth kernel and resolution | Ibrahim |
| Persistence, migrations and CI | Ernest |
| Contracts, OpenAPI and acceptance | Jacob |
| Nearby, WATCH and edge cases | RoboTech |

See `workstreams/README.md` for boundaries and handoffs.

## Read next

A new engineer should read only what is relevant to the task:

1. `TEAM_ONBOARDING_RUNBOOK.md`
2. `docs/ARCHITECTURE.md`
3. `docs/IMPLEMENTATION_STATUS.md`
4. `workstreams/README.md` and the assigned owner README
5. `docs/TESTING_STANDARD.md`
6. `docs/SECURITY_TEST_MATRIX.md` when touching auth, public DTOs, witness data, location, WATCH, or acquisition
7. `docs/ACCEPTANCE_TRACEABILITY.md` for requirement closure

The diagrams in `docs/diagrams/` are concise companion views of workflow, layers, and ownership.
