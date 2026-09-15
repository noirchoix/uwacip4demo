# Pipe 4 Feature Orchestration Map

This document maps each mobile-visible capability to the production layers that must cooperate. It is a guide to ownership and dependency direction, not permission to create feature-specific copies of the truth engine.

## 1. Current-state query

```text
GET /pipe4/current
  -> authenticated principal
  -> StateIdentity from query
  -> access/presentation policy
  -> CurrentStateRepository.get_current_state
  -> Knowledge public provenance labels (when visible)
  -> presentation mapper
  -> SuccessResponse[CurrentStatePresentation]
```

Primary: Victory (API/service), Ibrahim (status/presentation), Ernest (repository), Jacob (contract/security).

Key tests: known current, missing/UNKNOWN, stale, disputed, protected, unauthorized, nullable expiry/confidence.

## 2. Witness report — text

```text
POST /pipe4/witness/reports
  -> authenticated principal
  -> idempotency check
  -> optional entity resolution / provisional context
  -> Core AI interpretation (assistive only)
  -> build ObservationRecord
  -> persist observation
  -> Knowledge provenance on observation
  -> resolution / contradiction / verification policy
  -> optionally append StateVersion + move current projection
  -> safe domain event(s)
  -> WitnessReportReceipt ("You reported" != current state)
```

Primary: Victory. Truth decision: Ibrahim. Persistence: Ernest. Contract/privacy: Jacob.

Key tests: AI unavailable, AI misinterpretation, no entity yet, no location, duplicate idempotency key, observation saved without automatic publication, raw text absent from domain events.

## 3. Witness report — audio

```text
POST /pipe4/witness/audio-reports
  -> validate upload and size/type
  -> approved Core AI/STT boundary
  -> ordinary text-witness orchestration
```

There is **one witness state pipeline** after transcription. Do not maintain separate text and voice truth logic.

Primary: Victory + Jacob. Core AI boundary decision: Samuel.

## 4. Entity resolution / provisional reality

```text
POST /pipe4/entities/resolve
  -> EntityDirectoryPort
  -> candidates / resolved / no match

POST /pipe4/entities/provisional
  -> authenticated principal
  -> Pipe-4 provisional identity record
  -> PROVISIONAL status only
  -> future merge/link to canonical owner-module entity
```

Primary: Victory (owner-module boundary), Ernest (provisional persistence), Jacob (public contract).

Rule: a provisional record is not silently promoted into canonical Presence/Locator ownership.

## 5. Nearby

```text
GET /pipe4/nearby
  -> bounds + access filters
  -> CurrentStateRepository nearby query
  -> deterministic ranking signals
  -> rank_nearby()
  -> privacy-safe result DTOs
```

Primary: RoboTech. Persistence/query strategy: Ernest. Contract/security: Jacob.

Rule: `relevance_score` ranks discovery. It is not truth confidence.

## 6. WATCH

```text
create/list/pause/resume/delete
  -> authenticated principal
  -> canonical WatchCondition key
  -> repository

state publication event
  -> active WATCH candidates
  -> re-check authorization
  -> evaluate condition against exact StateVersion
  -> deduplicate transition/alert state
  -> Notification boundary
```

Primary: RoboTech + Victory. Persistence: Ernest. Acceptance/privacy: Jacob.

Rules: paused subscriptions never alert; permission changes must be respected at trigger time; equivalent watches should not create duplicate equivalent work.

## 7. Access request

```text
POST /pipe4/access-requests
  -> authenticated requester
  -> exact requested read scope
  -> PENDING request
  -> decision lifecycle
  -> approved scope used by current-state presentation
```

Primary: Ibrahim (lifecycle/policy), Victory (API/service), Jacob (authorization/IDOR tests), Ernest (persistence).

Rule: approval grants only the requested read scope. It does not establish truth or give write authority.

## 8. Targeted acquisition

```text
state gap / acquisition policy
  -> select eligible nearby target(s)
  -> privacy-safe offer
  -> user accepts or declines
  -> accepted request links into ordinary witness flow via targeted_request_id
  -> result is evidence, not automatic truth
```

Primary: RoboTech + Victory. Contract/privacy: Jacob. Persistence: Ernest.

Rule: targeted acquisition is opt-in and reuses the ordinary witness/evidence pipeline.

## Shared invariants across every feature

- no direct cross-module table writes;
- no provider SDKs under `current_state`;
- no mobile-generated canonical truth;
- no historical overwrite;
- no raw witness/audio/transcript in safe domain events;
- every public endpoint uses the host success/error envelope;
- every behavior lands with tests and acceptance traceability.
