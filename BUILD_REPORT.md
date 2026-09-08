# BUILD REPORT — UWACI Pipe 4 Production Reference v1.0

**Release date:** 2026-09-08  
**Standalone package:** `uwaci-pipe4-production-reference-v1.0.zip`  
**Mobile patch target:** `4c8951880cc50bfe2ccdb4b14e1b63acf1b0f375`

## 1. Release scope

This release contains the production reference implementation for Pipe 4 as an independently deployable FastAPI + PostgreSQL/PostGIS + Celery/Redis + SvelteKit system, together with the contract and integration handoff required to add the Pipe 4 mobile feature to the current UWACI mobile `origin/dev` baseline.

The release preserves the approved engineering invariants:

- one horizontal current-reality engine;
- exactly five core state domains: `AVAILABLE`, `ACCESSIBLE`, `WORKING`, `TIME`, `CHANGED`;
- observation is evidence, not automatic canonical state;
- declaration is not verification;
- inference is not observation;
- confidence is not authorization;
- UNKNOWN is a valid domain result and is never fabricated into a fake observation;
- append-preserving state history;
- provenance before confidence;
- permission lifecycle separate from physical/current reality;
- AI outside the canonical truth boundary;
- stable OpenAPI contracts;
- adapter/port boundaries for external systems and eventual UWACI backend integration.

## 2. Executed validation

| Validation | Result | Evidence |
|---|---|---|
| Python compilation | PASS | `python -m compileall -q src` |
| Backend test suite | PASS | **83 / 83 tests** |
| Baseline acceptance | PASS | AC-01 through AC-20 |
| MVP Addendum acceptance | PASS | ADD-AC-01 through ADD-AC-10 |
| Edge-case tests | PASS | 47 executable edge/invariant tests |
| Acceptance traceability | PASS | **70 / 70 IDs** present: 20 baseline + 10 addendum + EC-001–EC-040 |
| Strict policy validation | PASS | policy v1.0.0; all five core state domains |
| OpenAPI generation | PASS | `contracts/openapi/pipe4-v1.json` regenerated |
| OpenAPI drift check | PASS | generated schema matches committed contract after regeneration |
| Python wheel build | PASS | `uwaci_pipe4-1.0.0-py3-none-any.whl` |
| Mobile integration Git patch check | PASS | `git apply --check` against exact target commit |
| Mobile patch disposable apply | PASS | patch applied successfully to a pristine target copy |
| Mobile integration TS/TSX syntax | PASS | **24 files, 0 syntactic diagnostics** using TypeScript transpilation |
| Mobile overlay ZIP integrity | PASS | ZIP test completed with no corrupt member |
| Standalone ZIP integrity | Performed during final packaging | recorded in external checksum release step |

Backend collected-test breakdown:

```text
tests/test_acceptance_addendum.py: 10
tests/test_acceptance_baseline.py: 20
tests/test_api_contract.py: 3
tests/test_edge_cases.py: 47
tests/test_policy_domain.py: 3
TOTAL: 83
```

## 3. Environment-limited checks

The following checks are intentionally **not represented as PASS** because the required runtime/tooling is not available in this execution environment:

| Check | Status | Required follow-up |
|---|---|---|
| `ruff` | NOT EXECUTED — executable unavailable | run in CI or developer environment |
| `mypy` | NOT EXECUTED — executable unavailable | run in CI or developer environment |
| `pip-audit` | NOT EXECUTED — executable unavailable | run in CI with dependency/network access |
| Docker Compose runtime | NOT EXECUTED — Docker unavailable | run `docker compose up --build` on Docker host |
| SvelteKit `npm install/check/test/build` | NOT EXECUTED — package dependencies not installed and registry unavailable | clean install then `npm run check && npm run test && npm run build` |
| UWACI mobile full `npm run validate` | NOT EXECUTED — project dependencies not installed | run after applying patch and `npx expo install expo-location` |
| Native Expo location runtime | NOT EXECUTED — no device/Expo runtime | verify foreground permission, denial and fallback on device/simulator |
| Real UWACI backend adapters | BLOCKED — backend repository/source not supplied | perform R10 integration against actual backend |

These are release qualification items for CI/target infrastructure, not hidden passes.

## 4. Mobile integration

The mobile integration is generated against the exact repository baseline:

```text
4c8951880cc50bfe2ccdb4b14e1b63acf1b0f375
```

It preserves the current mobile architecture:

- Pipe 4 behavior remains under `src/features/pipe4`;
- existing `baseApi` remains the single RTK Query API root;
- auth remains centralized through the existing bearer-token header preparation;
- API responses retain the existing success/failure envelope;
- provider-specific AI logic remains server-side;
- native device location is exposed through a reusable `src/core/location` boundary;
- inference-first witness reporting is used;
- `None of these` creates provisional reality;
- “You reported” is separate from Uwaci canonical/current status;
- targeted acquisition reuses the ordinary witness reporting path.

The patch intentionally updates `package.json` but does **not** invent a lock-file integrity entry for `expo-location`. After applying, use:

```bash
npx expo install expo-location
npm run validate
```

## 5. Release qualification

This package is suitable as the Pipe 4 engineering reference/boilerplate for code review, implementation learning, edge-case development, and controlled integration work.

Before production deployment to an environment, run the environment-limited checks above and complete the real UWACI backend adapter integration when that backend source is available.
