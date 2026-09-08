# Pipe 4 System Context

Pipe 4 is an independently deployable reference service for current-reality resolution and a contract/adaptor source for UWACI integration. It is not a second competing implementation of UWACI Identity, Presence, Locator, Knowledge, Usage, Notification, or Core AI.

```text
Web / Mobile / Other Pipes
          |
       /api/v1
          |
   FastAPI application
          |
 application use cases
          |
  domain + typed policies
          |
 ports / repository protocols
     /         |          \
Postgres   Celery/Redis   external adapters
```

## Dependency law

`api/workers -> application -> domain + ports -> adapters/repositories`

The domain imports no FastAPI, SQLAlchemy, Celery, Redis, object-store, identity-provider, or LLM SDK.

## Truth boundary

Observation, declaration, inference, verification, and publication are separate operations. AI output can propose structure but cannot create provenance or VERIFIED state.
