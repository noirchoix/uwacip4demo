# UWACI Pipe 4 — Production Reference Service

Production-shaped standalone implementation of UWACI Pipe 4: Current Reality & State Completion.

This repository intentionally provides two outputs:

1. **Standalone reference system** — FastAPI + PostgreSQL/PostGIS + Celery/Redis + SvelteKit.
2. **UWACI integration handoff** — contract/adapter guidance plus a mobile integration patch generated against the uploaded `origin/dev` baseline.

## Design laws

- One horizontal current-reality engine.
- State domains are exactly `AVAILABLE`, `ACCESSIBLE`, `WORKING`, `TIME`, `CHANGED`.
- Observation is evidence, not canonical truth.
- Declaration is not verification.
- Inference is not observation.
- Confidence is not authorization.
- UNKNOWN is valid and must never be fabricated into a fake observation.
- Provenance precedes confidence.
- Published state history is append-preserving.
- AI is optional and constrained to interpretation; structured retrieval works without AI.
- External systems are accessed through ports/adapters.
- No vertical state engines or cross-system table writes.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Web: `http://localhost:3000`  
API: `http://localhost:8000/api/v1/health/live`  
OpenAPI (development): `http://localhost:8000/docs`

## Development

Backend:

```bash
cd apps/api
python -m venv .venv
# activate it
pip install -e ".[dev]"
pytest
ruff check .
mypy src
```

Web:

```bash
cd apps/web
npm install
npm run check
npm run test
npm run build
```

## Contract

The backend OpenAPI document is the contract authority. Run:

```bash
python scripts/export_openapi.py
python scripts/check_openapi_drift.py
```

## Engineering reference

See:

- `docs/architecture/`
- `docs/adr/`
- `docs/acceptance/`
- `PIPE4_PRODUCTION_BUILD_MANIFEST_v1.0.md`
