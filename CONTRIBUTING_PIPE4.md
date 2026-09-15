# Pipe 4 Contribution Workflow

This file supplements the host repository's `CONTRIBUTING.md`. The current `uwaci-backend` repository remains authoritative for branch and CI commands.

## Before coding

1. sync `dev`;
2. create one focused branch;
3. read your `workstreams/<owner>/README.md`;
4. identify acceptance IDs affected;
5. write the first failing behavior test.

## During implementation

Preserve dependency direction:

```text
API -> services -> domain + ports
adapters/repositories -> ports + owner-module public interfaces
```

Do not:

- write another module's tables directly;
- add provider SDKs to `current_state`;
- add Redis, Celery, PostGIS, or other infrastructure without a demonstrated host requirement and reviewed decision;
- turn Nearby relevance into truth confidence;
- expose raw witness/source metadata in public DTOs;
- put business policy in FastAPI route functions;
- overwrite historical state instead of appending a version.

## PR evidence

Every PR should state:

- workstream and owner;
- behavior/acceptance IDs addressed;
- focused tests added and the RED failure reason;
- quality gates run;
- API/OpenAPI impact;
- migration/persistence impact;
- security/privacy impact;
- owner-module dependencies;
- unresolved gaps.

Shared contracts or cross-workstream interfaces require Samuel review before dependent branches diverge. PRs target `dev`; repository maintainers retain merge authority.
