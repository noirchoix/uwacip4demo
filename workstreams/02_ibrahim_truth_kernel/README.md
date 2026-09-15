# Ibrahim — Truth Kernel & Resolution

## Production destination paths

```text
app/modules/current_state/domain/
app/modules/current_state/services/resolution.py
app/modules/current_state/services/presentation.py
```

## Primary tasks

- protect exact five state types;
- finalize canonical StateIdentity rules;
- typed state values and validation;
- observation lifecycle invariants;
- state-version lifecycle transitions;
- freshness/stale/expired semantics;
- contradiction handling;
- verification-to-publication rules;
- UNKNOWN and user-facing presentation status;
- guarantee observation != publication.

## Key design constraint

Do not build a universal opaque `confidence = 0.73` truth engine. Knowledge confidence is optional source context. If a future Pipe 4 confidence model is approved, it must be separately named, documented, calibrated and tested.

## Tests to own

- identity collision/qualifier cases;
- partial quantity truth;
- time/range values;
- illegal lifecycle transitions;
- contradictory verified observations;
- stale and expired state;
- AI interpretation rejected/misinterpreted;
- missing state remains UNKNOWN.

## Shared contract seam

Treat typed WATCH/access value objects and atomic publication semantics as shared domain contracts. If a
truth-kernel change needs a new WATCH operator, access-scope dimension or publication invariant, coordinate
with Jacob/Ernest and obtain Samuel review rather than widening the contract locally.
