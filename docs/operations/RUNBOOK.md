# Operations Runbook

## Local/reference startup

```bash
cp .env.example .env
docker compose up --build
```

Expected services: Postgres/PostGIS, Redis, API, Celery worker, Celery beat, SvelteKit web.

## Health

- `/api/v1/health/live` — process liveness.
- `/api/v1/health/ready` — dependency readiness.
- `/api/v1/metrics` — development/reference metrics endpoint; protect or move to platform metrics in production.

## Failure behavior

- AI outage must not block structured current-state reads.
- One failed acquisition source escalates to another qualifying source within job deadline.
- All-source failure ends in UNKNOWN, not an invented answer.
- Outbox sweep retries unpublished domain events.

## Production checklist

- Replace development secrets.
- Configure JWT issuer/audience/JWKS.
- Configure R2/S3 evidence store.
- Restrict CORS.
- Disable public docs as configured.
- Run migrations before traffic.
- Connect structured logs/metrics/alerts.
- Configure backups for PostgreSQL and object storage.
