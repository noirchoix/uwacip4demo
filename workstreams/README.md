# Pipe 4 Workstream Index

These directories define **coordination ownership**, not runtime package boundaries.
Production code remains under the normal UWACI backend paths.

| Workstream | Primary owner | Primary production paths | First integration dependency |
|---|---|---|---|
| Integration authority | Samuel | shared interfaces / ADRs / review | all workstreams |
| Service/API composition | Victory Azundo | `api/`, `services/`, `adapters/` | Ibrahim + Jacob |
| Truth kernel & resolution | Ibrahim | `domain/`, resolution/presentation policy | Ernest |
| Persistence, migrations & CI | Ernest | `models/`, `repositories/`, migrations | Ibrahim |
| Contracts, OpenAPI & acceptance | Jacob | `schemas/`, contract/acceptance tests | Victory |
| Nearby, WATCH & edge cases | RoboTech | Nearby/WATCH domain/services/tests | Ibrahim + Ernest |

## Shared interface rule

A workstream may propose a shared interface, but dependent teams do not fork independent versions of the
same contract. Samuel reviews shared interface changes before parallel branches depend on them.

## Handoff minimum

Every workstream handoff includes:

1. production paths changed;
2. acceptance IDs addressed;
3. tests added and RED failure observed;
4. public interface changes;
5. migration/data implications;
6. privacy/security implications;
7. unresolved dependencies.
