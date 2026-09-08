# UWACI PIPE 4 — Production Reference Service & Integration Build Manifest
**Version:** 1.0  
**Date:** 8 September 2026  
**Status:** Approved build baseline for implementation planning  
**Primary goal:** Build one production-grade, independently deployable Pipe 4 reference system (FastAPI + SvelteKit) and one integration/handoff layer for the evolving UWACI application, without maintaining two different Pipe 4 domain implementations.

---

## 1. Executive Build Decision

The system will be built as:

1. **A standalone Pipe 4 reference service**
   - Production FastAPI API.
   - PostgreSQL/PostGIS persistence.
   - Durable asynchronous acquisition/verification jobs.
   - Versioned policy engine.
   - R2/S3-compatible evidence storage boundary.
   - Production SvelteKit web application.
   - Full acceptance, failure, security, contract, and performance test suite.
   - Independently deployable with Docker Compose for local/reference operation.

2. **A UWACI integration package**
   - Mobile feature integration into the existing Expo/React Native repository.
   - OpenAPI-derived typed client contracts.
   - Adapters/contracts for UWACI Identity, Knowledge, Presence, Locator, Core AI, Usage, Notification, and events.
   - Cross-Pipe query/event proof without direct foreign-table writes.
   - No second implementation of Pipe 4 business logic.

The standalone service is intentionally independent. The production domain core must therefore depend on **ports**, not on UWACI-internal models or vendor SDKs. The UWACI handoff supplies adapters to those ports.

### Non-negotiable engineering laws

- One horizontal engine; no industry-specific state engines.
- `AVAILABLE`, `ACCESSIBLE`, `WORKING`, `TIME`, and `CHANGED` are the five canonical state domains.
- Observation is evidence; it is not automatically canonical current state.
- Declaration is not verification.
- Inference is not observation.
- Confidence is not authorization.
- UNKNOWN is a valid result; do not fabricate a state row merely to return an answer.
- History is append-preserving.
- Provenance precedes confidence.
- State version/time must remain referenceable by consequential consumers.
- Permission state is separate from physical/current reality.
- AI is optional and advisory for structured interpretation; deterministic state retrieval must not depend on an LLM.
- Cross-system integration uses stable contracts/IDs/events, never convenience writes into foreign tables.
- New infrastructure must solve a demonstrated problem; no Kafka, Kubernetes, graph DB, agent framework, or microservice multiplication by default.
- “Better” implementations must be demonstrated through simpler invariants, stronger tests, lower risk, or measurable operational improvement—not asserted.

---

## 2. Source Authority

The following source order governs implementation decisions:

1. Approved Pipe 4 Current Reality & State Completion Requirements v0.3.
2. Approved Pipe 4 MVP Requirements Addendum v0.1.
3. Pipe 4 Developer Onboarding & Implementation Guide v1.0.
4. Existing UWACI architecture/ownership rules where source code is available.
5. Current `dev` branch of the uploaded UWACI mobile repository.
6. Active feature branches as compatibility context only.
7. Previous Pipe 4 backend/demo/mobile implementation as a proven behavioral baseline.
8. FastAPI, SvelteKit/TypeScript, AI-engineering, clean-code, and code-review guidance as engineering rules/heuristics.

Feature-branch code is not automatically authoritative. If it conflicts with approved requirements, the requirements win. If it conflicts with stable project architecture, an ADR/owner decision is required.

---

## 3. Repository Archaeology

### 3.1 Previous Pipe 4 backend

Reviewed reference:
`uwaci-pipe4-backend-addendum-v0.1.1`

Observed implementation:
- Python/FastAPI modular package `src/uwaci_pipe4`.
- PostgreSQL/PostGIS through SQLAlchemy/Alembic.
- Redis + Celery worker/beat.
- Transactional outbox.
- R2/local evidence store adapters.
- Supabase/JWT-capable auth adapter.
- Baseline API plus mobile-facing `/api/v1/pipe4` contract.
- 37 automated tests:
  - AC-01 through AC-20.
  - ADD-AC-01 through ADD-AC-10.
  - Seven additional invariant/infrastructure tests.
- Original vanilla static UI.
- Later SvelteKit UI overlay developed separately.

### 3.2 Previous SvelteKit overlay

The SvelteKit overlay introduced useful presentation concepts:
- `DecisionSummary`
- `EvidencePanel`
- `WorkflowModel`
- `EventTimeline`
- `CollapsiblePanel`
- `TechnicalDetails`
- user-friendly decision translation instead of raw backend payloads

It remains a **presentation prototype**, not the final web architecture:
- mostly one page;
- large global stylesheet;
- manually maintained types;
- static adapter/FastAPI-serving topology;
- developer/demo concerns mixed into the user-facing surface.

The components/presentation ideas should be selectively retained, but the SvelteKit application should be rebuilt around production routes, strict TypeScript, runtime API validation, typed server/client boundaries, and adapter-node deployment.

### 3.3 Uploaded UWACI repository

The uploaded Git clone is the **UWACI mobile repository**. It is a real clone with branch history and remotes, but the inspected repository contains **no FastAPI/Python/Alembic backend source**. Therefore:

- mobile integration can be designed and later validated against this repository now;
- backend ownership/adapters can be specified from the Developer Guide;
- actual compile/test integration against the UWACI backend monolith remains blocked until that backend repository/source is supplied.

This is an explicit release gate, not a reason to block the standalone service.

### 3.4 Mobile branch state

| Branch | Head | Base relative to `origin/dev` | Integration meaning |
|---|---|---|---|
| `origin/dev` | `4c89518` | current | Canonical mobile baseline |
| `feature/profile-backend-and-account-deletion` | `674bada` | current dev | Useful live backend/auth/error-integration pattern |
| `feature/pipe-2-screens-8-9` | `5fd5daa` | current dev | UI context only; no authoritative Pipe 2 API contract |
| `feature/matching-engine-screens` | `e83c005` | older dev base | UI context; not stable backend contract |
| `feature/matching-domain-types` | `bbd5df4` | older dev base | Provisional matching types/contracts |
| `feature/matching-need-presence-screens` | `b4ff648` | older dev base | Explicitly provisional Need/Presence/Match contract |
| `feature/communications-channel` | `c95d561` | old main base | Stale for Pipe 4 integration decisions |

### 3.5 Mobile contracts that are already sufficiently stable to respect

From current `dev`:
- Expo Router routes remain thin.
- Dependency direction: `routes -> features -> core/shared`; core never imports feature internals.
- Pipe 4 is already a recognized `PipeId`, but is `available: false`.
- One RTK Query `baseApi` uses `${API_BASE_URL}/api/v1`.
- Bearer token comes from Supabase session via `prepareHeaders`.
- API envelope is:
  - success: `{ success: true, data, meta: { request_id, timestamp? } }`
  - failure: `{ success: false, error: { code, message, details? }, meta }`
- Mobile does not own provider AI integrations.
- Usage/credit authority is server-side.
- Zod already exists in the repository.
- The current mobile repo has `expo-image-picker` but no `expo-location`.

### 3.6 Provisional cross-Pipe context

The matching feature branch explicitly marks its Need/Presence API contract as provisional. Its `Presence` currently contains:
- location;
- availability window;
- quantity;
- status;
- `freshnessConfirmedAt`;
- provenance.

These fields overlap conceptually with Pipe 4 but are **not authoritative Pipe 4 contracts**. Pipe 4 must not implement itself around these provisional TypeScript types.

The future integration seam should instead use:
- canonical entity/presence IDs;
- `StateIdentity`;
- exact `state_version_id`;
- observation/validity time;
- current-state presentation;
- revalidation contract.

Presence remains the owner of stable declared presence/product/service data; Pipe 4 owns current-reality resolution in the standalone reference implementation and maps to the approved backend ownership boundary during monolith integration.

---

## 4. Old Implementation Disposition

### 4.1 Retain as engineering logic, with limited cleanup

| Old file | Disposition | New destination / treatment |
|---|---|---|
| `domain/canonical.py` | **RETAIN** | `domain/state/identity.py`; preserve deterministic canonical JSON + fingerprinting |
| `policies/contradiction.py` | **RETAIN/REFINE** | `domain/policies/contradiction.py`; preserve material-conflict logic, add policy-version coverage |
| `policies/corroboration.py` | **RETAIN/REFINE** | `domain/policies/corroboration.py`; preserve independent-origin checks |
| `policies/decision.py` | **RETAIN/REFINE** | `domain/policies/decision.py`; preserve decision-context separation |
| `policies/freshness.py` | **RETAIN/REFINE** | `domain/policies/freshness.py`; preserve decay semantics and timezone-aware evaluation |
| `policies/identity.py` | **RETAIN/REFINE** | `domain/state/identity.py`; enforce explicit five-domain policy registration |
| `policies/source_ranking.py` | **RETAIN/REFINE** | `domain/policies/source_ranking.py`; retain hard admissibility filters before soft score |
| `policies/transitions.py` | **RETAIN/REFINE** | split state/request/observation transition policies |
| `policies/verification.py` | **RETAIN/REFINE** | `domain/policies/verification.py`; preserve inference rejection and contradiction checks |
| `policies/watch.py` | **RETAIN** | `domain/watch/predicate.py`; retain deterministic predicate semantics |
| `infrastructure/object_store.py` | **RETAIN CONCEPT** | `adapters/evidence/{local,s3}.py`; narrow storage port, streaming/hash verification |
| `workers/tasks.py` | **RETAIN PATTERN** | split durable acquisition, verification, expiry, and outbox tasks |
| `workers/celery_app.py` | **RETAIN FOR STANDALONE** | production-configured Celery app; non-root container; explicit queues/retry policy |
| transactional outbox logic | **RETAIN** | make it a formal standalone-service ADR and atomic persistence invariant |
| AC/ADD-AC tests | **RETAIN AS ORACLE** | rewrite/expand under `tests/acceptance` using production modules |

### 4.2 Refactor substantially

| Old file | Reason | Required refactor |
|---|---|---|
| `domain/enums.py` | too many unrelated enums in one file; no strong `StateType` | split by domain; introduce enum with exactly five core state types |
| `domain/models.py` | 400+ LOC mixed aggregate DTOs and `Any` values | split aggregates; introduce typed/discriminated state value envelope |
| `policies/confidence.py` | hard-coded evidence strengths/weights | externalize/version policy; keep explainable breakdown; add calibration fixtures |
| `policies/registry.py` | silently invents defaults for unknown state type | strict schema validation; no silent state-type fallback |
| `policies/security.py` | local role/tag semantics | replace with `AuthorizationPort`; standalone and UWACI adapters derive authority server-side |
| `services/orchestrator.py` | ~745 LOC god service | decompose into focused use cases |
| `services/addendum_service.py` | ~707 LOC mixed access/witness/nearby/entity/acquisition | decompose by capability |
| `services/watch_service.py` | useful but tightly coupled to repository/service | separate watch application use cases + shared process coordinator |
| `services/events.py` | concrete local implementation | make event publisher/event log ports explicit |
| `api/router.py` | 365 LOC mixed legacy/demo/public/internal endpoints | replace with route-family modules |
| `api/mobile_router.py` | 387 LOC, useful contract but too monolithic | split under `/api/v1/pipe4`, preserve compatible paths where sensible |
| `api/schemas.py` / `mobile_schemas.py` | duplicated public schemas | one API contract layer, separate create/read/internal DTOs |
| `api/auth.py` | provider details mixed with principal model | move to standalone auth adapter; routes depend on authenticated principal dependency |
| `repositories/base.py` | giant repository surface | split repository ports by aggregate/use case |
| `repositories/sqlalchemy_repo.py` | 500 LOC and sync persistence | use SQLAlchemy 2 async, explicit transactions, focused repositories |
| `infrastructure/db_models.py` | all rows in one module | split persistence models by aggregate |
| `integrations/ai_gateway.py` | placeholder contract too narrow | typed `AIInterpretationPort`; deterministic parser first, AI fallback |
| `integrations/cross_pipe.py` | fake internal principal and demo-only call path | replace with stable query/revalidate/event integration contracts |
| `demo_scenarios.py` | embedded in production service layer | move to developer fixtures/acceptance scenarios |
| `config/policies.yaml` | missing `CHANGED`; nearby factors incomplete | replace with validated versioned policy bundle |

### 4.3 Remove from production runtime

| Old element | Action |
|---|---|
| `static/index.html`, `static/app.js`, `static/styles.css` | remove |
| duplicate default architectural API surface | remove from public API |
| public CRUD for demo `Entity`/`Source` management | move to protected developer fixtures or admin tooling |
| `repositories/memory.py` | test fake only |
| package/project naming containing `architectural_demo` | remove |
| FastAPI serving the SvelteKit production app | remove; separate web/API processes |
| raw developer event/metrics payloads on consumer surfaces | move behind protected developer/admin interfaces |
| Redis Pub/Sub as if it were durable event truth | remove as durability assumption; DB/outbox remains durable truth |

---

## 5. Required Corrections From the Baseline

### 5.1 State type is not free text

Production introduces:

```python
class StateType(StrEnum):
    AVAILABLE = "AVAILABLE"
    ACCESSIBLE = "ACCESSIBLE"
    WORKING = "WORKING"
    TIME = "TIME"
    CHANGED = "CHANGED"
```

Unknown state domains do not silently receive default policies. A new industry maps into these domains through identity qualifiers/value semantics/policies; it does not invent `AGRICULTURE_CAPACITY` as a sixth state engine.

### 5.2 `CHANGED` receives an explicit policy

The previous policy file omitted `CHANGED`. Production must define:
- freshness/decay;
- material-change equivalence window;
- allowed value semantics;
- contradiction behavior;
- evidence/verification requirements.

### 5.3 No silent policy fallback

Policy loading is strict:
- validate YAML/JSON against Pydantic schema at startup;
- require all five core state types;
- validate every decision context;
- validate weight sum/range as appropriate;
- calculate policy bundle hash/version;
- persist policy version/hash on consequential state publication.

A typo or unsupported state type fails closed.

### 5.4 Confidence is versioned policy, not magic code

The previous `ConfidenceEngine` concept is retained, but:
- evidence strengths and factor weights are configuration;
- factors are independently observable;
- final score includes a `ConfidenceBreakdown`;
- decision threshold is separate;
- verification policy is separate;
- confidence never directly grants access or authority;
- test fixtures cover calibration monotonicity and contradictory inputs.

### 5.5 Nearby ranking is completed

Ranking factors:
- proximity;
- intent/context relevance;
- urgency;
- consequence of uncertainty;
- freshness;
- confidence;
- recent material change;
- active demand;
- watch relevance.

Hard permission/admissibility filters run **before** ranking.

### 5.6 Natural-language report flow becomes inference-first

Target UX/system flow:

```text
raw text/voice + available location
        ↓
deterministic extraction for obvious patterns
        ↓
typed AI interpretation only when deterministic parsing is insufficient
        ↓
entity/state/value candidates
        ↓
high confidence → confirm smallest necessary detail
low confidence  → one focused clarification
        ↓
None of these → provisional reality
        ↓
ObservationRecord
        ↓
verification/reconciliation
        ↓
optional StateVersion publication
```

The user does not have to manually choose a state domain when Uwaci can infer it reliably.

### 5.7 UNKNOWN is not a fabricated StateVersion

Absence/failure is represented through:
- no eligible current state;
- `StateRequest`/gap outcome;
- `CurrentStatePresentation(kind=UNKNOWN, status=UNKNOWN|VERIFYING)`.

Do not create fake coordinates, observation timestamps, verification timestamps, or `INFERRED` provenance just to satisfy a state schema.

### 5.8 Baseline lifecycle is represented across separate aggregates

The conceptual requirements lifecycle:

```text
UNKNOWN → REQUESTED → OBSERVED/DECLARED/IMPORTED/INFERRED
→ VERIFICATION_PENDING → CURRENT → DISPUTED → STALE → EXPIRED → REPLACED
```

is implemented without overloading one enum:

- **Resolution/request status:** REQUESTED, ACQUIRING, VERIFYING, RESOLVED, UNKNOWN, FAILED/TIMED_OUT.
- **Observation status:** RECEIVED, INTERPRETED, ENTITY_RESOLVED, ACCEPTED_AS_EVIDENCE, VERIFYING, CONSUMED, REJECTED.
- **Epistemic status:** DECLARED, OBSERVED, SYSTEM_REPORTED, TRANSACTION_EVIDENCED, INFERRED, VERIFIED.
- **Verification status:** UNVERIFIED, PENDING, VERIFIED, FAILED, INCONCLUSIVE.
- **Published StateVersion lifecycle:** CURRENT, DISPUTED, STALE, EXPIRED, REPLACED.
- **User-facing status:** CURRENT, VERIFYING, DISPUTED, STALE, INFERRED, UNKNOWN.

This preserves the requirements lifecycle while preventing the `VERIFICATION_PENDING`/`CURRENT` conflation seen in weaker designs.

---

## 6. Final Standalone Repository Topology

```text
uwaci-pipe4/
├── README.md
├── Makefile
├── .env.example
├── compose.yaml
├── package.json                         # workspace helper scripts only
│
├── apps/
│   ├── api/
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   ├── migrations/
│   │   │   └── versions/
│   │   ├── src/
│   │   │   └── pipe4/
│   │   │       ├── __init__.py
│   │   │       ├── app.py
│   │   │       ├── config.py
│   │   │       ├── logging.py
│   │   │       ├── exceptions.py
│   │   │       │
│   │   │       ├── api/
│   │   │       │   ├── dependencies.py
│   │   │       │   ├── errors.py
│   │   │       │   ├── envelope.py
│   │   │       │   └── v1/
│   │   │       │       ├── health.py
│   │   │       │       ├── current_state.py
│   │   │       │       ├── declarations.py
│   │   │       │       ├── observations.py
│   │   │       │       ├── state_requests.py
│   │   │       │       ├── disputes.py
│   │   │       │       ├── refresh.py
│   │   │       │       ├── revalidation.py
│   │   │       │       ├── watches.py
│   │   │       │       ├── access_requests.py
│   │   │       │       ├── nearby.py
│   │   │       │       ├── witness.py
│   │   │       │       ├── entity_resolution.py
│   │   │       │       ├── acquisition_requests.py
│   │   │       │       └── internal.py
│   │   │       │
│   │   │       ├── domain/
│   │   │       │   ├── state/
│   │   │       │   │   ├── enums.py
│   │   │       │   │   ├── values.py
│   │   │       │   │   ├── identity.py
│   │   │       │   │   ├── models.py
│   │   │       │   │   └── transitions.py
│   │   │       │   ├── observation/
│   │   │       │   ├── acquisition/
│   │   │       │   ├── watch/
│   │   │       │   ├── access/
│   │   │       │   ├── evidence/
│   │   │       │   ├── events/
│   │   │       │   └── policies/
│   │   │       │       ├── types.py
│   │   │       │       ├── freshness.py
│   │   │       │       ├── confidence.py
│   │   │       │       ├── corroboration.py
│   │   │       │       ├── contradiction.py
│   │   │       │       ├── verification.py
│   │   │       │       ├── decision.py
│   │   │       │       ├── source_ranking.py
│   │   │       │       └── nearby_ranking.py
│   │   │       │
│   │   │       ├── application/
│   │   │       │   ├── current_state/
│   │   │       │   │   ├── get_current_state.py
│   │   │       │   │   ├── publish_state.py
│   │   │       │   │   ├── declare_state.py
│   │   │       │   │   ├── observe_state.py
│   │   │       │   │   ├── request_state.py
│   │   │       │   │   └── revalidate_state.py
│   │   │       │   ├── acquisition/
│   │   │       │   ├── verification/
│   │   │       │   ├── watches/
│   │   │       │   ├── access/
│   │   │       │   ├── witness/
│   │   │       │   └── nearby/
│   │   │       │
│   │   │       ├── ports/
│   │   │       │   ├── authorization.py
│   │   │       │   ├── entities.py
│   │   │       │   ├── locator.py
│   │   │       │   ├── provenance.py
│   │   │       │   ├── sources.py
│   │   │       │   ├── acquisition.py
│   │   │       │   ├── ai.py
│   │   │       │   ├── evidence_store.py
│   │   │       │   ├── notification.py
│   │   │       │   ├── usage.py
│   │   │       │   ├── events.py
│   │   │       │   ├── jobs.py
│   │   │       │   └── clock.py
│   │   │       │
│   │   │       ├── repositories/
│   │   │       │   ├── state.py
│   │   │       │   ├── observation.py
│   │   │       │   ├── request.py
│   │   │       │   ├── watch.py
│   │   │       │   ├── access.py
│   │   │       │   ├── acquisition.py
│   │   │       │   └── events.py
│   │   │       │
│   │   │       ├── adapters/
│   │   │       │   ├── persistence/
│   │   │       │   ├── auth/
│   │   │       │   ├── evidence/
│   │   │       │   ├── ai/
│   │   │       │   ├── events/
│   │   │       │   ├── jobs/
│   │   │       │   └── standalone/
│   │   │       │
│   │   │       ├── observability/
│   │   │       └── workers/
│   │   │
│   │   └── tests/
│   │       ├── unit/
│   │       ├── integration/
│   │       ├── contract/
│   │       ├── acceptance/
│   │       ├── edge_cases/
│   │       ├── security/
│   │       └── performance/
│   │
│   └── web/
│       ├── package.json
│       ├── svelte.config.js
│       ├── vite.config.ts
│       ├── tsconfig.json
│       └── src/
│           ├── hooks.server.ts
│           ├── app.d.ts
│           ├── routes/
│           └── lib/
│               ├── api/
│               ├── schemas/
│               ├── types/
│               ├── components/
│               └── features/
│
├── config/
│   └── policies/
│       ├── pipe4-policy.v1.yaml
│       └── schema.json
│
├── contracts/
│   └── openapi/
│       └── pipe4-v1.json
│
├── integration/
│   ├── uwaci-mobile/
│   └── uwaci-backend/
│
├── infra/
│   ├── docker/
│   ├── reverse-proxy/
│   └── observability/
│
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── contracts/
│   ├── engineering/
│   ├── acceptance/
│   └── operations/
│
└── scripts/
    ├── export_openapi.py
    ├── check_openapi_drift.py
    ├── validate_policy.py
    └── validate_acceptance_trace.py
```

### Dependency direction

```text
API / workers
      ↓
application use cases
      ↓
domain + ports
      ↓
adapters / repositories
```

Domain code never imports:
- FastAPI;
- SQLAlchemy;
- Redis/Celery;
- boto3/R2 SDK;
- Supabase SDK;
- LLM/STT provider SDK;
- Expo/mobile code.

---

## 7. Port / Adapter Contract Manifest

| Port | Domain purpose | Standalone adapter | UWACI integration adapter |
|---|---|---|---|
| `AuthorizationPort` | object-level view/declare/verify/decide permissions | JWT/OIDC principal + local memberships | Identity contract |
| `EntityCatalogPort` | canonical/provisional entity resolution | local reference entity registry | Presence/approved owner module |
| `LocatorPort` | canonical location refs + spatial lookup | PostGIS/reference entity geometry | Locator contract |
| `ProvenancePort` | evidence/provenance attachments, trust context | local provenance implementation | Knowledge contract |
| `SourceRegistryPort` | source capabilities/reliability context | local source profile tables | Knowledge/source contract |
| `AcquisitionSourcePort` | acquire one state from a qualifying source | connector registry | approved UWACI/provider connectors |
| `AIInterpretationPort` | typed text/audio interpretation proposal | provider-neutral AIGateway adapter | Core AI AIGateway |
| `EvidenceStorePort` | write/read evidence objects by opaque ref | local/R2/S3 | UWACI storage boundary |
| `NotificationPort` | notification handoff | event/in-app adapter | Notification contract |
| `UsagePort` | quota/rate/credit decision | standalone rate policy | Usage contract |
| `EventPublisherPort` | domain state/access/watch events | transactional outbox publisher | UWACI event contract |
| `JobSchedulerPort` | durable async work | Celery/Redis | approved UWACI worker |
| `Clock` | trusted server time for testability | UTC system clock | injected clock |
| repository ports | Pipe4-owned persistence | async SQLAlchemy/Postgres | local current-state module repositories if integrated |

### Acquisition connector rule

Source connectors implement one narrow protocol:

```python
class AcquisitionSourcePort(Protocol):
    async def capabilities(self, identity: StateIdentity) -> SourceCapability: ...
    async def acquire(self, request: AcquisitionRequest) -> AcquisitionResult: ...
```

Source selection is separate from source execution. The ranking engine chooses from capability metadata; connectors do not decide whether their own evidence becomes canonical state.

---

## 8. Domain Model Manifest

### 8.1 State identity

Canonical identity includes:
- `entity_id`
- `object_key`
- `state_type`
- `location_key` when truth differs by location
- policy-approved truth-defining qualifiers

It explicitly excludes:
- requester ID;
- decision context;
- requested quantity unless quantity defines the truth being asserted;
- display name alone;
- presentation-only filters.

Identity fingerprint uses deterministic canonical serialization and SHA-256.

### 8.2 State values

Replace unconstrained `Any` with a typed value envelope. Initial value kinds:

- `BooleanStateValue`
- `QuantityStateValue`
- `DurationStateValue`
- `RangeStateValue`
- `ChangeStateValue`
- `CategoricalStateValue`

State policy declares allowed value kinds for each of the five state domains.

Example horizontal reuse:

```text
AVAILABLE + BooleanStateValue(true)
AVAILABLE + QuantityStateValue(available=12, unit="tonne")
TIME      + RangeStateValue(min=900, max=1500, unit="second")
WORKING   + BooleanStateValue(false)
CHANGED   + ChangeStateValue(changed=true, category="service_interruption")
```

This supports the cold-storage capacity test without creating a new state engine.

### 8.3 Core aggregates

- `StateVersion`
- `CurrentStateProjection`
- `ObservationRecord`
- `EvidenceRecord`
- `StateRequest`
- `AcquisitionJob`
- `AcquisitionAttempt`
- `ContradictionRecord`
- `WatchProcess`
- `WatchSubscription`
- `AccessRequest`
- `PermissionGrant`
- `TargetedAcquisitionRequest`
- `DomainEvent`

### 8.4 Current-state presentation

Stable public DTO:

```text
CurrentStatePresentation
  kind: STATE | PROTECTED | UNKNOWN
  status: CURRENT | VERIFYING | DISPUTED | STALE | INFERRED | UNKNOWN
  entity_summary
  state_type?
  value?
  observed_at?
  expires_at?
  freshness?
  confidence?
  epistemic_status?
  verification_status?
  provenance_summary?
  state_version_id?
  actions[]
```

Rules:
- PROTECTED does not expose the hidden value, timestamps, confidence, source, or diagnostic hints unless explicitly safe.
- UNKNOWN contains no fabricated state metadata.
- VERIFYING may coexist with a user’s newly submitted observation while current canonical state remains unchanged.
- UI text/icons carry meaning; color is supplementary.

---

## 9. Database Ownership Manifest — Standalone Service

### 9.1 Pipe 4-owned tables

1. `state_version`
   - immutable published state versions
   - predecessor/replacement relationship
   - state identity fields
   - typed JSON value
   - lifecycle/epistemic/verification status
   - confidence + policy version
   - observed/valid/expiry/verification timestamps
   - visibility
   - correlation ID

2. `current_state_projection`
   - one row per canonical state identity key
   - points to current `state_version_id`
   - atomically updated with state publication/outbox

3. `observation`
   - raw structured observation
   - original `observed_at`
   - server `received_at`
   - client-reported time where relevant
   - location evidence/accuracy/manual description
   - private actor/source ref
   - observation status
   - consumed state version when applicable

4. `evidence_metadata`
   - opaque evidence ID
   - content hash
   - object-store key/ref
   - evidence class
   - source ref
   - origin ref for independence/dedup
   - captured/received times
   - safe metadata
   - no binary blobs

5. `state_evidence_link`
   - many-to-many state-version/evidence references

6. `state_request`
   - reality gap/request lifecycle
   - decision context
   - request fingerprint for dedup
   - terminal UNKNOWN/RESOLVED outcome

7. `acquisition_job`
   - one shared resolution job
   - timeout/deadline
   - status
   - idempotency key
   - selected policy version

8. `acquisition_attempt`
   - source attempt
   - started/completed time
   - outcome/reason
   - cost/latency
   - evidence/result refs

9. `contradiction`
   - competing state/evidence refs
   - materiality
   - resolution status
   - created/resolved timestamps

10. `watch_process`
    - canonical normalized watch fingerprint
    - shared underlying evaluation/acquisition process

11. `watch_subscription`
    - subscriber-specific state
    - ACTIVE/ALERTING/PAUSED
    - permission scope/ref
    - last-trigger context

12. `access_request`
    - PENDING/APPROVED/DENIED/REVOKED/EXPIRED/CANCELLED
    - requester/decider refs
    - requested/granted scope
    - audit timestamps

13. `permission_grant`
    - effective approved access scope
    - expiration/revocation lineage

14. `targeted_acquisition_request`
    - gap ref
    - target user ref
    - OFFERED/ACCEPTED/DECLINED/EXPIRED/COMPLETED
    - optional real reward assignment only

15. `source_profile` **standalone adapter only**
    - source type/capabilities
    - global baseline reliability
    - response/cost metadata

16. `source_reliability_outcome` **standalone adapter only**
    - source × entity × state-type outcome history

17. `reference_entity` **standalone adapter only**
    - canonical reference ID
    - display metadata
    - PostGIS point/area where useful
    - resolved/provisional state
    - no implication that this table replaces UWACI Presence/Locator

18. `reference_entity_alias` **standalone adapter only**

19. `domain_event`
    - append event ledger for audit/replay/consumer proof

20. `outbox`
    - transactionally committed events awaiting publication

21. `idempotency_record`
    - scoped operation/actor/idempotency key/result hash

### 9.2 Not stored as canonical DB ownership

- raw media binary;
- provider AI responses as state truth;
- mobile user profiles;
- UWACI Presence/Product/Location copies in the integrated deployment;
- payment/transaction settlement data;
- notification delivery state owned by external Notification adapter.

### 9.3 UWACI integration ownership mapping

When integrated into the real backend:
- Identity replaces standalone membership/authorization authority.
- Presence/approved owner module replaces `reference_entity` canonical ownership.
- Locator replaces canonical location ownership.
- Knowledge replaces standalone provenance/source-trust authority.
- Core AI replaces standalone AI provider orchestration.
- Usage replaces standalone usage policy.
- Notification owns delivery.
- the approved current-state module owns only the universal current-state/resolution records.

---

## 10. Standalone Infrastructure Decisions

### 10.1 PostgreSQL/PostGIS
**Selected.**
- state/history durability;
- spatial nearby queries;
- transaction boundaries;
- outbox atomicity.

### 10.2 Celery + Redis
**Selected for the standalone reference service**, recorded by ADR.

Reason:
- external acquisition and verification may be slow/unreliable;
- retry/backoff/idempotency are mandatory;
- scheduled expiry/refresh is required;
- the previous build already proves this stack;
- switching frameworks adds risk without current evidence of a better fit.

Rules:
- one worker framework only;
- separate queues only when workload isolation is demonstrated;
- worker never bypasses normal application transition services;
- non-root containers;
- bounded retries;
- dead/final failure is explicit;
- queue depth/failure metrics.

### 10.3 Transactional outbox
**Selected.**
State mutation and consequential event record commit in one DB transaction.

Low-latency optimization:
- after successful commit, enqueue outbox dispatch best-effort;
- periodic sweep is the crash-recovery fallback;
- dispatcher logs empty polls only at debug level;
- Redis Pub/Sub may accelerate live developer/SSE views but is never event durability.

### 10.4 SvelteKit
**Selected as a separate production web process.**
- adapter-node;
- FastAPI remains domain API under `/api/v1`;
- reverse proxy exposes web under `/` and API under `/api/v1`;
- no FastAPI StaticFiles mounting for production.

### 10.5 No additional distributed infrastructure
Do not add:
- Kafka;
- RabbitMQ in addition to Redis/Celery;
- Kubernetes requirement;
- Neo4j;
- service mesh;
- agent framework;
- separate ML service;
unless a later ADR includes measured evidence.

---

## 11. API Contract Manifest

### 11.1 Standard envelope

Success:

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO-8601"
  }
}
```

Failure:

```json
{
  "success": false,
  "error": {
    "code": "PIPE4_STABLE_CODE",
    "message": "safe human message",
    "details": {}
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO-8601"
  }
}
```

### 11.2 Public/mobile API

#### Health
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`

#### Current state
- `GET /api/v1/pipe4/current`
- `GET /api/v1/pipe4/history`
- `POST /api/v1/pipe4/revalidate`

#### Declaration / structured observation
- `POST /api/v1/pipe4/declarations`
- `POST /api/v1/pipe4/observations`

#### Reality gaps / state requests
- `POST /api/v1/pipe4/state-requests`
- `GET /api/v1/pipe4/state-requests/{request_id}`
- `POST /api/v1/pipe4/refresh-requests`

#### Disputes
- `POST /api/v1/pipe4/disputes`

#### Nearby
- `GET /api/v1/pipe4/nearby`

#### Access requests
- `POST /api/v1/pipe4/access-requests`
- `GET /api/v1/pipe4/access-requests`
- `GET /api/v1/pipe4/access-requests/{id}`
- `POST /api/v1/pipe4/access-requests/{id}/approve`
- `POST /api/v1/pipe4/access-requests/{id}/deny`
- `POST /api/v1/pipe4/access-requests/{id}/revoke`
- `POST /api/v1/pipe4/access-requests/{id}/cancel`

#### Watches
- `POST /api/v1/pipe4/watches`
- `GET /api/v1/pipe4/watches`
- `GET /api/v1/pipe4/watches/{id}`
- `DELETE /api/v1/pipe4/watches/{id}`
- `POST /api/v1/pipe4/watches/{id}/pause`
- `POST /api/v1/pipe4/watches/{id}/resume`

#### Witness reporting
- `POST /api/v1/pipe4/witness/interpret`
- `POST /api/v1/pipe4/witness/reports`
- `POST /api/v1/pipe4/witness/audio-reports`

#### Entity resolution
- `POST /api/v1/pipe4/entities/resolve`
- `POST /api/v1/pipe4/entities/provisional`

#### Targeted acquisition
- `POST /api/v1/pipe4/acquisition-requests`
- `GET /api/v1/pipe4/acquisition-requests`
- `GET /api/v1/pipe4/acquisition-requests/{id}`
- `POST /api/v1/pipe4/acquisition-requests/{id}/accept`
- `POST /api/v1/pipe4/acquisition-requests/{id}/decline`

### 11.3 Protected internal/admin capabilities

Capabilities required by baseline but not appropriate as ordinary consumer mutations:

- verify state/evidence;
- explicitly expire state;
- record source outcome;
- ingest authenticated system/transaction observations;
- replay/reconcile jobs;
- inspect full provenance;
- inspect event ledger.

Expose under a protected internal contract such as:

- `POST /api/v1/internal/pipe4/verifications`
- `POST /api/v1/internal/pipe4/state-versions/{id}/expire`
- `POST /api/v1/internal/pipe4/source-outcomes`
- `POST /api/v1/internal/pipe4/system-observations`
- `GET /api/v1/internal/pipe4/state-versions/{id}`
- `GET /api/v1/internal/pipe4/events`

No authority is accepted from client-supplied user/role IDs. Principal and service authority are server-derived.

### 11.4 OpenAPI is the contract authority

Build output:
`contracts/openapi/pipe4-v1.json`

CI:
1. boot FastAPI app;
2. export OpenAPI deterministically;
3. compare with committed contract;
4. intentional changes require contract update + consumer impact note.

Mobile and SvelteKit types are generated/validated from this contract rather than maintained independently.

---

## 12. SvelteKit Web Manifest

### 12.1 Production routes

```text
/                         Current Reality overview / entry point
/nearby                   Mixed-domain nearby current states
/reality/[stateKey]       One canonical current-state detail
/report                   Natural text/voice witness reporting
/following                All Watches
/access                   Access-request list/status
/requests                 Targeted acquisition requests
/developer                Protected developer workspace
/developer/scenarios      Horizontal/acceptance demos
/developer/events         Event/outbox inspection
/developer/policies       Active policy versions/explainability
```

### 12.2 Feature modules

```text
src/lib/features/current-state/
src/lib/features/nearby/
src/lib/features/witness-reporting/
src/lib/features/watches/
src/lib/features/access/
src/lib/features/acquisition/
src/lib/features/developer/
```

### 12.3 Presentation rules

Primary hierarchy:

```text
entity/object
    ↓
what is true now?
    ↓
how recent?
    ↓
how certain / how established?
    ↓
what can the user do?
    ↓
optional evidence/developer detail
```

User surfaces must not lead with:
- state IDs;
- raw enums;
- JSON payloads;
- policy hashes;
- source-ranking internals.

Developer details remain available in bounded/collapsible technical panels.

### 12.4 Required UI states

Every query/mutation implements:
- loading;
- empty;
- success;
- stale;
- disputed;
- protected;
- verifying;
- unknown;
- validation error;
- unexpected error;
- offline/network degraded.

Color never carries state meaning alone.

### 12.5 Type/runtime rules

- strict TypeScript;
- Svelte 5 typed props/runes for new components;
- no `any` at API boundaries;
- Zod/runtime validation of API responses where useful;
- server-only secrets/session logic remain in server files;
- no provider SDK from client;
- Playwright critical-path tests;
- accessibility checks.

---

## 13. UWACI Mobile Integration Manifest

### 13.1 Integration location

Add Pipe 4 under:

```text
src/features/pipe4/
```

Never under `src/core`.

Thin route files live in `app/`.

### 13.2 Required feature areas

```text
src/features/pipe4/
├── api/
│   ├── generated.ts
│   ├── schemas.ts
│   ├── pipe4Api.ts
│   └── witnessAudioUpload.ts
├── components/
├── hooks/
├── screens/
├── types/
└── index.ts
```

### 13.3 Base API integration

- inject endpoints into existing `baseApi`;
- extend tag types intentionally for Pipe4 state/watches/access/acquisition;
- retain current bearer-token `prepareHeaders`;
- retain the existing success/error envelope;
- map errors through core error policy;
- do not maintain a second global API client.

### 13.4 Navigation integration

Current `dev` already includes `pipe4` as a `PipeId`.

Integration will:
- enable `pipe4`;
- provide Pipe 4-specific footer/navigation:
  - Home
  - Nearby
  - Following
  - Report
  - Menu
- extend footer IDs only where necessary;
- keep route files thin;
- avoid duplicating current pipe route state in Redux.

### 13.5 Native location

Do not ship `navigator.geolocation` as the final React Native mechanism.

Add `expo-location` through the project-supported Expo install flow and wrap it behind a small core platform abstraction because location is reusable platform capability.

Pipe 4 consumes:
- permission status;
- coordinates;
- accuracy;
- failure/denial.

Pipe 4 owns:
- the fallback UX;
- manual location description;
- how location evidence affects the observation.

### 13.6 Witness flow correction

Do not require entity selection before natural report.

Target:
1. user reports text/voice;
2. device location is attached when allowed;
3. backend interprets likely entity/state/value;
4. high-confidence candidate asks minimal confirmation;
5. ambiguity asks one focused question;
6. None of these creates provisional reality;
7. observation submitted;
8. receipt shows `You reported` separately from `Uwaci status`.

### 13.7 Matching/Pipe 1 interaction

The current matching branch is provisional. Integration therefore must not import matching feature internals.

Future contract:
- Pipe 1 passes canonical entity/presence ID + state request identity.
- Pipe 4 returns state version/time/presentation.
- Pipe 1 remains matching/ranking owner.
- consequential action may call revalidate with the exact `state_version_id`.

### 13.8 Pipe 2/3 interaction

Current uploaded branches do not provide stable Pipe2/Pipe3 backend contracts.

For the reference release:
- define protocol fixtures and cross-pipe contract tests;
- do not couple to UI branch shapes;
- implement one real integration when the actual backend contract is available.

---

## 14. AI Engineering Manifest

### 14.1 Minimum Sufficient Mechanism

Order of preference:

1. database constraint / typed data model;
2. deterministic rule;
3. versioned policy;
4. established algorithm;
5. existing service/infrastructure;
6. constrained AI only if the above do not sufficiently solve the problem.

### 14.2 AI-free core paths

AI is forbidden as a dependency for:
- current-state GET;
- freshness;
- expiration;
- permission checks;
- state identity;
- state transitions;
- contradiction eligibility;
- watch predicate evaluation;
- watch fingerprinting;
- current projection;
- history retrieval;
- idempotency;
- access-request lifecycle.

### 14.3 AI-permitted paths

AI may propose:
- state type/value extraction from natural language;
- entity/object hints;
- temporal interpretation;
- evidence classification;
- concise operator explanation.

Requirements:
- typed input/output schema;
- model/provider hidden behind `AIInterpretationPort`;
- original evidence linked;
- malformed output rejected;
- low-confidence clarification;
- model version/prompt version logged;
- no direct publish/verify authority;
- AI outage fallback tested.

### 14.4 Deterministic parser first

Obvious phrases such as:
- “not working”
- “closed”
- “available”
- “wait is about 20 minutes”

should first pass through inexpensive deterministic extraction where sufficiently reliable. AI is fallback/augmentation, not a mandatory hop.

---

## 15. Acceptance-Test Matrix

### 15.1 Baseline gates

| Gate | Primary production proof | Main modules | Target release |
|---|---|---|---|
| AC-01 | fresh trusted GET avoids acquisition | current-state + freshness | R3 |
| AC-02 | missing GET/request creates shared gap | request/acquisition | R4 |
| AC-03 | successful acquisition creates structured evidence-backed state | acquisition/publish/provenance | R5 |
| AC-04 | all sources fail → UNKNOWN, no fabricated state | acquisition/presentation | R5 |
| AC-05 | expired state never silently current | freshness/presentation | R4 |
| AC-06 | material credible conflict → DISPUTED with both evidence sets | contradiction/publish | R4 |
| AC-07 | replacement preserves predecessor/history | persistence/publish | R2 |
| AC-08 | offline observed time independent of received time | observation/persistence | R3 |
| AC-09 | AI cannot manufacture VERIFIED | AI adapter/verification | R6 |
| AC-10 | AI down, structured GET works | current-state + failure tests | R6 |
| AC-11 | protected state does not leak via API/nearby/AI/watch | authorization/presentation | R6 |
| AC-12 | one Pipe1/2/3 consumer queries common contract | integration | R9/R10 |
| AC-13 | state-change event consumed across Pipe boundary | events/integration | R9/R10 |
| AC-14 | watch triggers event when condition becomes true | watch/events | R6 |
| AC-15 | equivalent watches share one process | watch process | R6 |
| AC-16 | confirmed outcome updates source reliability | provenance/source outcomes | R6 |
| AC-17 | historical fields support future freshness learning | schema/history | R2 |
| AC-18 | AVAILABLE/TIME/WORKING run through same engine | acceptance scenarios | R8 |
| AC-19 | authorized audit explains who/what/when/evidence | provenance/internal audit | R8 |
| AC-20 | CURRENT/UNKNOWN/STALE/DISPUTED/INFERRED survive distinctly | domain/presentation | R8 |

### 15.2 Addendum gates

| Gate | Primary production proof | Main modules | Target release |
|---|---|---|---|
| ADD-AC-01 | protected access PENDING → APPROVED/DENIED without leakage | access/authorization | R6 |
| ADD-AC-02 | one mixed-domain nearby ranking path | nearby/PostGIS | R6 |
| ADD-AC-03 | list/open/pause/resume/remove watches | watches | R6 |
| ADD-AC-04 | public evidence only Witness N labels | provenance/presentation | R6 |
| ADD-AC-05 | natural text/voice report + inferred state domain + device location | witness/AI/location | R6/R7 |
| ADD-AC-06 | location retry/manual fallback still submits | witness/location | R6/R7 |
| ADD-AC-07 | None-of-these → provisional, no overwrite | entity resolution | R6 |
| ADD-AC-08 | “You reported” + separate “Uwaci VERIFYING” | observation/presentation | R6/R7 |
| ADD-AC-09 | targeted request accept/decline; accept reuses witness flow | acquisition/witness | R6 |
| ADD-AC-10 | one UI/API presentation renders 3+ unrelated domains | presentation/web/mobile | R7/R9 |

### 15.3 Edge-case test groups

All EC-001–EC-040 must receive an explicit test ID in `docs/acceptance/edge-case-traceability.md`.

Test files are grouped by failure mechanism rather than by vertical:

```text
tests/edge_cases/test_temporal_integrity.py       # EC-001, 002, 010, 011, 025–027, 030
tests/edge_cases/test_source_adversarial.py       # EC-003–008, 024, 031, 032, 039
tests/edge_cases/test_failure_recovery.py         # EC-012–016
tests/edge_cases/test_identity_value_semantics.py # EC-017–023, 035, 036
tests/edge_cases/test_scale_dedup.py               # EC-028, 029
tests/edge_cases/test_permission.py                # EC-033, 034
tests/edge_cases/test_cross_pipe.py                # EC-037, 038
tests/edge_cases/test_economics.py                 # EC-040
```

---

## 16. Build Order / Release Manifest

## R0 — Archaeology, contracts, ADR freeze

**Create**
- `docs/architecture/system-context.md`
- `docs/architecture/domain-semantics.md`
- `docs/architecture/integration-context.md`
- `docs/adr/0001-standalone-reference-and-adapter-boundary.md`
- `docs/adr/0002-state-semantics-and-unknown.md`
- `docs/adr/0003-state-identity.md`
- `docs/adr/0004-transactional-outbox.md`
- `docs/adr/0005-celery-redis-worker.md`
- `docs/adr/0006-evidence-storage.md`
- `docs/adr/0007-policy-versioning.md`
- `docs/adr/0008-api-openapi-contract.md`
- `docs/adr/0009-web-api-auth-topology.md`
- `docs/adr/0010-uwaci-ownership-mapping.md`
- `config/policies/pipe4-policy.v1.yaml`
- policy Pydantic schema/tests

**Must be true before R1**
- five state types explicitly registered;
- `CHANGED` policy exists;
- no silent state-type fallback;
- standalone vs UWACI ownership boundary documented;
- worker/outbox decision recorded;
- no unresolved meaning for Observation vs StateVersion vs VERIFYING.

---

## R1 — Domain kernel

**Build**
- `domain/state/enums.py`
- `domain/state/values.py`
- `domain/state/identity.py`
- `domain/state/models.py`
- `domain/state/transitions.py`
- observation/access/watch/acquisition domain models
- policy types and pure engines
- clock port

**Tests**
- deterministic identity;
- truth qualifiers;
- value-kind validation;
- legal transitions fail closed;
- policy bundle startup validation;
- confidence monotonicity/traceability;
- independent corroboration;
- source hard filter;
- watch predicate/fingerprint.

**Exit gate**
- domain has zero FastAPI/SQLAlchemy/Celery/provider imports;
- unit tests green;
- one cold-storage capacity example works without new engine.

---

## R2 — Persistence + event integrity

**Build**
- async SQLAlchemy models/repositories;
- Alembic 0001 core state/evidence/history;
- Alembic 0002 request/watch/access/acquisition;
- current-state projection;
- transaction service;
- domain event + outbox;
- idempotency records.

**Tests**
- migration upgrade/downgrade;
- snapshot/history atomicity;
- state replacement preserves history;
- state+outbox atomic commit;
- idempotent duplicate write;
- concurrent publication/unique current identity;
- timezone-aware timestamps.

**Exit gate**
- no destructive state overwrite;
- no cross-aggregate partial commit;
- DB integration tests against real Postgres/PostGIS.

---

## R3 — Core API: GET / DECLARE / OBSERVE

**Build**
- app factory;
- config/logging/error envelope/request IDs;
- auth principal dependency;
- current state route;
- declaration route;
- structured observation route;
- history;
- OpenAPI export;
- current-state presentation.

**Tests**
- 401/403/404/409/422 contract behavior;
- no client-supplied authority;
- fresh GET;
- declaration != verification;
- observation does not auto-publish;
- offline observed/received times;
- protected presentation leakage tests.

**Exit gate**
- AC-01, AC-07, AC-08 foundations demonstrated;
- OpenAPI committed and contract-tested;
- known fresh GET performance smoke <500 ms backend target.

---

## R4 — Gap resolution / freshness / contradiction

**Build**
- StateRequest;
- shared request fingerprint;
- decision context;
- freshness;
- contradiction assessment;
- revalidate endpoint;
- source capability/ranking plan;
- refresh request.

**Tests**
- missing/stale/disputed paths;
- request dedup;
- material vs temporal non-contradiction;
- quantity/variant/location semantics;
- high-consequence revalidation;
- no forced false precision for TIME.

**Exit gate**
- AC-02, AC-05, AC-06 behavior complete without external acquisition.

---

## R5 — Durable acquisition / evidence / workers

**Build**
- evidence store port + local/S3/R2 adapters;
- source connector protocol;
- acquisition job/attempt;
- Celery jobs;
- retry/backoff/timeout/escalation;
- outbox dispatcher;
- expiry/refresh worker;
- source-failure terminal UNKNOWN.

**Tests**
- source succeeds;
- source times out then escalates;
- every source fails;
- duplicate delivery;
- worker restart;
- evidence hash;
- outbox recovery;
- no indefinite request.

**Exit gate**
- AC-03, AC-04;
- API never blocks indefinitely on slow acquisition;
- worker can restart without duplicate state publication.

---

## R6 — Addendum + security + AI boundary

**Build**
- access request lifecycle;
- permission grants;
- All Watches + shared processes;
- nearby horizontal ranking;
- witness pseudonyms;
- entity resolution/provisional registry;
- targeted acquisition;
- deterministic witness parser;
- typed AI interpretation adapter;
- audio evidence processing;
- source outcome/reliability update;
- internal verification APIs.

**Tests**
- AC-09–AC-11, AC-14–AC-16;
- ADD-AC-01–09;
- AI provider down;
- AI hallucinated source rejected;
- revoked permission stops WATCH;
- duplicate evidence/independence;
- location denied/manual fallback;
- no reward invention.

**Exit gate**
- all backend addendum semantics complete except final rich UI proof.

---

## R7 — Production SvelteKit web

**Build**
- adapter-node SvelteKit shell;
- server auth/session boundary;
- API client generated from OpenAPI;
- runtime schemas;
- current-state components;
- nearby;
- report;
- following;
- access;
- targeted requests;
- developer scenarios/events/policies.

**Tests**
- component states;
- accessibility;
- no raw protected metadata;
- report-vs-current-state;
- Playwright critical flows;
- Svelte check/lint/build.

**Exit gate**
- ADD-AC-10 demonstrated in web;
- user-facing UI does not expose raw backend internals;
- developer console remains protected.

---

## R8 — Full standalone hardening

**Build**
- metrics/logging/tracing;
- `/health/live`, `/health/ready`;
- rate limiting;
- structured audit;
- backup/restore notes;
- container hardening;
- reverse proxy;
- security headers;
- deployment runbook;
- full acceptance traceability.

**Tests**
- all AC-01–20;
- all ADD-AC-01–10;
- all EC-001–040 mapped;
- security leakage suite;
- performance/load smoke;
- clean Compose rebuild.

**Exit gate**
- standalone reference system is the team boilerplate.

---

## R9 — UWACI mobile handoff

**Build against current `dev`**
- `src/features/pipe4`;
- RTK Query endpoints;
- generated types/runtime schemas;
- route files;
- pipe4 navigation/footer;
- `expo-location` platform adapter;
- witness text/voice;
- Nearby/Following/Access/Requests;
- current-state presentation;
- localization;
- mobile contract tests.

**Integration checks**
- current baseApi envelope preserved;
- auth bearer preserved;
- core never imports Pipe 4;
- no provider secret/client AI calls;
- mobile does not calculate trust/confidence/credits;
- no matching-feature internal dependency.

**Exit gate**
- mobile `validate` passes;
- ADD-AC-02/03/05/06/08/09/10 proven on mobile;
- integration overlay applies cleanly to target commit.

---

## R10 — Real UWACI backend integration

**Blocked until backend repository/source is supplied.**

Then:
- inspect current dev backend, owner modules, events, dependencies, migrations;
- implement Identity/Knowledge/Presence/Locator/CoreAI/Usage/Notification adapters;
- decide current-state persistence ownership via ADR;
- map transactional/event behavior to host architecture without duplicating worker systems;
- implement one real Pipe1/2/3 query consumer;
- implement one state-change event consumer;
- state-version revalidation contract;
- run monolith contract/integration tests.

**Exit gate**
- AC-12 and AC-13 proven against real UWACI backend;
- no foreign table writes;
- no duplicate trust/location/user/product systems.

---

## 17. Quality Gates for Every Pull Request

### Backend
- Ruff format/check.
- strict mypy.
- pytest relevant unit/integration/contract tests.
- migration test if schema touched.
- pip-audit.
- OpenAPI drift check if contract touched.
- Docker build smoke if runtime/dependency changed.
- failure-path test for any external dependency or async workflow.

### SvelteKit
- clean install.
- `svelte-check`.
- ESLint.
- Prettier check.
- unit/component tests.
- Playwright for critical flow changes.
- production build.

### Mobile
- follow repository `npm run validate`.
- Expo dependency compatibility check when adding native package.
- tests for route/navigation/API change.
- no feature-to-feature internal dependency.

### Review questions
Every PR must answer:
1. Which requirement/acceptance/edge-case ID does this implement?
2. Which aggregate/module owns every field/table changed?
3. Which invariant could this change violate?
4. What happens when DB/source/AI/worker/network fails?
5. What is the permission/privacy impact?
6. Does it create new infrastructure/dependency? Why is that necessary now?
7. What proves idempotency/concurrency safety where relevant?
8. Does it change OpenAPI or mobile consumers?
9. Can the author explain the AI-assisted code without relying on the model output?

---

## 18. Release-Level Definition of “Best-Fit”

The build is accepted as the team standard only when all seven dimensions pass:

1. **Specification**
   - AC-01–20 and ADD-AC-01–10.
   - horizontal cold-storage acceptance test.

2. **Domain correctness**
   - no fabricated reality;
   - uncertainty survives;
   - history/provenance survives;
   - observation/inference/declaration/verification remain distinct.

3. **Architecture**
   - clear dependency direction;
   - provider-neutral domain;
   - ports at external boundaries;
   - no vertical state engines;
   - no duplicate UWACI ownership in integration.

4. **Software engineering**
   - typed contracts;
   - cohesive use cases;
   - no god services;
   - no magic policy numbers scattered in code;
   - explicit transactions;
   - bounded I/O;
   - pagination where needed;
   - no N+1 hot paths.

5. **Security/privacy**
   - server-derived authority;
   - object-level authorization;
   - no protected-state leakage;
   - witness pseudonymization;
   - precise contributor location private;
   - safe logs/errors.

6. **Operations**
   - health/readiness;
   - structured logging/request IDs;
   - metrics;
   - queue visibility;
   - retry/backoff;
   - non-root containers;
   - reproducible Compose path.

7. **Integration**
   - committed OpenAPI;
   - mobile contract tests;
   - cross-Pipe state version/revalidation;
   - adapter-level integration with real UWACI owner modules when backend is available.

---

## 19. Explicitly Deferred Until Evidence Requires It

- deep reputation dashboards;
- source-forensics console beyond required audit;
- complex enterprise approval chains;
- reward marketplace/accounting;
- advanced ranking personalization;
- predictive freshness ML;
- custom model training;
- autonomous agents;
- Kafka;
- Kubernetes requirement;
- Neo4j;
- arbitrary vertical dashboards;
- distributed microservices inside Pipe 4.

---

## 20. Immediate Implementation Entry Point

Implementation starts at **R0**, not by editing the old orchestrator.

The first code-producing sequence is:

```text
policy schema + five state types
        ↓
StateIdentity + typed StateValue
        ↓
StateVersion / Observation / Request separation
        ↓
pure policy tests
        ↓
Postgres persistence + current projection + outbox
        ↓
GET / DECLARE / OBSERVE
```

The previous implementation remains the acceptance oracle and source of proven mechanisms, but the production repository is built deliberately around the architecture above rather than mechanically refactoring the old folder tree.

The final R0 artifact must freeze enough decisions that the later implementation can be divided into engineering layers without each developer inventing a different interpretation of Pipe 4.
