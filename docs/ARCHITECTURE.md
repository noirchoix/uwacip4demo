# Pipe 4 Backend-Native Architecture

```text
uwaci-mobile
    |
    | /api/v1/pipe4
    v
current_state.api           thin HTTP boundary
    |
    v
current_state.services      orchestration / policies / use cases
    |
    +------> current_state.domain         pure state semantics
    |
    +------> current_state.ports          owner-module boundaries
    |            |
    |            +--> Identity
    |            +--> Knowledge
    |            +--> Core AI
    |            +--> Notification
    |            +--> Locator / Presence
    |
    v
current_state.repositories  Pipe-4-owned persistence only
    |
    v
PostgreSQL / SQLAlchemy / Alembic
```

## Dependency direction

```text
API -> services -> domain + ports
repositories/adapters -> domain + ports
external owner modules never import current_state internals
```

The domain core never imports FastAPI, SQLAlchemy, provider SDKs, Redis, Celery or the mobile client.

## Persistence ownership

Pipe 4 may own:

- observations;
- published state versions;
- current-state projection/pointer;
- state-version ↔ observation links;
- access requests specific to current-state reads;
- WATCH subscriptions;
- targeted acquisition requests;
- provisional entity-resolution records pending canonical ownership.

Pipe 4 does **not** own:

- user/auth identity;
- canonical organizations/memberships;
- generic provenance/source-trust authority;
- AI providers;
- notification delivery infrastructure;
- canonical Presence/Locator records.

## Promotion flow

```text
observation received
      |
      +--> Knowledge provenance attached to observation
      |
      +--> resolution / contradiction / freshness checks
                    |
             +------+------+
             |             |
        insufficient    policy permits
        / disputed      publication
             |             |
        VERIFYING /     append StateVersion
        DISPUTED            |
                            v
                    atomically move current
                    projection pointer
```

A state version is never edited into a new truth. New truth = new version.

## Confidence

`confidence` is not an authorization decision and is not automatically computed as a universal probability. It is nullable. Nearby ranking uses a separate `relevance_score` and explicit ranking breakdown.
