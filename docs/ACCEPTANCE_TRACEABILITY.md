# Pipe 4 Acceptance Traceability

Status values in this file are intentionally conservative:

- `REFERENCE`: part of the behavior is demonstrated by the starter kernel/tests, but host integration is not complete.
- `TODO`: requires implementation in the real backend.
- `BLOCKED`: depends on an owner-module/environment decision that must not be fabricated locally.
- `PROVEN`: may only be used after the named production/acceptance test passes in the integrated backend.

Mark a gate `PROVEN` only after the named integrated production/acceptance test passes.

## Baseline acceptance gates

| ID | Requirement | Primary owner(s) | Starter proof / planned test | Status |
|---|---|---|---|---|
| AC-01 | Fresh Known State | Ibrahim, Victory, Jacob | presentation + current query acceptance test | REFERENCE |
| AC-02 | Missing State | Ibrahim, Jacob | `test_missing_state_is_unknown` + API UNKNOWN case | REFERENCE |
| AC-03 | Successful Acquisition | Victory, RoboTech, Jacob | acquisition service + endpoint acceptance | TODO |
| AC-04 | Complete Acquisition Failure | Victory, RoboTech, Jacob | failure-to-UNKNOWN acceptance | TODO |
| AC-05 | Stale State | Ibrahim, Jacob | `test_expired_timestamp_is_presented_as_stale` + API case | REFERENCE |
| AC-06 | Contradiction | Ibrahim, Jacob | `test_contradiction_blocks_publication_even_if_verified` + history case | REFERENCE |
| AC-07 | State Transition | Ibrahim, Ernest | transition + append-version repository tests | REFERENCE |
| AC-08 | Offline Observation | Victory, Ernest, Jacob | delayed/offline observation integration test | TODO |
| AC-09 | AI Boundary | Victory, Samuel | typed Core AI adapter; AI never canonical | TODO |
| AC-10 | AI Outage | Victory, Jacob | AI failure degrades safely without fabricated truth | TODO |
| AC-11 | Permission Boundary | Victory, Jacob, Samuel | auth/IDOR/protected-state contract tests | TODO |
| AC-12 | Cross-Pipe Query | Samuel, Victory | version-addressable public service contract | TODO |
| AC-13 | Cross-Pipe Event | Samuel, Victory | host `DomainEvent` integration test | TODO |
| AC-14 | WATCH | RoboTech, Victory, Jacob | lifecycle + trigger + notification tests | REFERENCE |
| AC-15 | WATCH Aggregation | RoboTech, Ernest | canonical-key deduplication / load behavior | REFERENCE |
| AC-16 | Source Learning | RoboTech, Samuel | telemetry/event readiness without learned truth authority | TODO |
| AC-17 | Freshness Learning Readiness | RoboTech, Ibrahim | explicit freshness/outcome telemetry | TODO |
| AC-18 | Horizontal Demonstration | Samuel, Jacob | same engine across all five state types | TODO |
| AC-19 | Provenance | Victory, Ernest, Jacob | Knowledge provenance-per-observation integration | TODO |
| AC-20 | Uncertainty Survival | Ibrahim, Jacob | UNKNOWN/VERIFYING/DISPUTED survive API presentation | REFERENCE |

## MVP addendum gates

| ID | Requirement | Primary owner(s) | Starter proof / planned test | Status |
|---|---|---|---|---|
| ADD-AC-01 | Access request lifecycle | Ibrahim, Victory, Jacob | access transition tests + endpoint/auth tests | REFERENCE |
| ADD-AC-02 | Mixed-domain nearby discovery | RoboTech, Ernest, Jacob | deterministic ranking + repository/API test | REFERENCE |
| ADD-AC-03 | All WATCHes management | RoboTech, Victory, Jacob | create/list/pause/resume/delete contract suite | TODO |
| ADD-AC-04 | Witness pseudonymization | Victory, Jacob | public provenance DTO privacy test | TODO |
| ADD-AC-05 | Natural-language witness report | Victory, Jacob | Core AI interpretation + ordinary observation flow | TODO |
| ADD-AC-06 | Location fallback | Victory, Jacob | no-location/manual-description acceptance | TODO |
| ADD-AC-07 | None-of-these provisional reality | Victory, Ernest, Jacob | provisional entity contract + persistence/API test | REFERENCE |
| ADD-AC-08 | Reported observation vs Uwaci current state | Ibrahim, Victory, Jacob | separate receipt/current-state acceptance | REFERENCE |
| ADD-AC-09 | Targeted nearby acquisition | RoboTech, Victory, Jacob | opt-in + `targeted_request_id` ordinary witness path | TODO |
| ADD-AC-10 | Universal current-state presentation | Ibrahim, Victory, Jacob | one renderer across five state types | REFERENCE |

## Edge-case families

The required edge cases are grouped by engineering concern and owner.

| Family | IDs | Primary owner(s) | Required proof |
|---|---|---|---|
| time/freshness/races | EC-001, 002, 010, 011, 023, 025, 026, 027, 030, 037 | Ibrahim, Ernest, RoboTech | deterministic clock/time tests + concurrent repository tests |
| conflicting/manipulated evidence | EC-003..008, 024, 038, 039 | Ibrahim, Victory, RoboTech | contradiction, provenance, spoof/manipulation tests |
| acquisition/source/AI failure | EC-012..016, 031, 032, 040 | Victory, RoboTech, Samuel | graceful degradation; no fabricated source/truth |
| identity/location/variant/quantity | EC-009, 017..022, 035, 036 | Ibrahim, RoboTech, Jacob | identity + typed value + location fallback tests |
| demand/WATCH/permission | EC-028, 029, 033, 034 | RoboTech, Ernest, Jacob | dedupe, authorization re-check, load/idempotency tests |

## Update rule

Each PR that closes or materially advances an acceptance ID must update this file with the exact production test path. Do not mark an ID `PROVEN` from a unit test alone when the requirement is integration- or acceptance-level.
