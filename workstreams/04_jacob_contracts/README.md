# Jacob — Contracts, OpenAPI & Acceptance

## Production destination paths

```text
app/modules/current_state/schemas/
app/modules/current_state/api/openapi.py
tests/contract/
tests/integration/
docs/implementation/
```

## Primary tasks

- keep Pydantic response/request schemas aligned to mobile TypeScript;
- create OpenAPI documentation/operation IDs;
- add contract tests for all mobile-used endpoints;
- preserve canonical success/error envelope;
- test auth failure, forbidden/protected/unknown behavior;
- verify privacy-safe DTOs and witness pseudonymization;
- maintain acceptance traceability.

## Known contract corrections

Review `patches/mobile-contract-backend-truth.patch`:

- nullable state confidence;
- nullable expiry;
- optional entity ID at witness boundary;
- targeted acquisition ID on witness report;
- explicit WATCH operator/scalar target types;
- typed access permission/scope and approved scope.

## Anti-patterns

- partial response mocks;
- assertions that only prove a fake was called;
- accepting backend/mobile drift because TypeScript says `unknown`;
- exposing internal source identifiers/provider names to public DTOs.

## Shared contract freeze

The mobile patch now also narrows WATCH to the approved operator/scalar-target vocabulary and access
requests to `READ` + typed `Pipe4AccessScope`, including `approved_scope`. Keep OpenAPI and TypeScript in
lockstep; do not widen fields back to arbitrary `string`, `unknown` or `Record<string, unknown>` for
convenience.
