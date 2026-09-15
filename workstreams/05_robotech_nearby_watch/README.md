# RoboTech — Nearby, WATCH & Edge Cases

## Production destination paths

```text
app/modules/current_state/services/nearby.py
app/modules/current_state/services/watch.py
app/modules/current_state/domain/nearby.py
app/modules/current_state/domain/watch.py
tests/unit/current_state/
tests/integration/current_state/
```

## Primary tasks

- deterministic Nearby ranking;
- mixed-domain Nearby behavior;
- repository-level geo strategy with Ernest;
- WATCH canonicalization and trigger evaluation;
- freshness/source/outcome telemetry design;
- adversarial and edge-case coverage;
- future ML readiness without inserting ML into canonical truth this week.

## ML boundary

Machine learning may later help source ranking, freshness estimation, anomaly detection or acquisition prioritization, but the first increment must be deterministic and explainable. No learned model decides canonical truth without an approved evaluation/calibration path.

## Tests to own

- Nearby ordering stable for equal inputs;
- distance unavailable fallback;
- stale result ranking;
- WATCH duplicate equivalence;
- paused WATCH never notifies;
- permission change after subscription;
- state changes before notification;
- demand spikes do not create duplicate equivalent work.

## Shared ranking/WATCH contract

Use/inject the named `NearbyRankingPolicy`; do not duplicate numeric weights in orchestration code. Additional requirement-defined signals remain zero-weight until intentionally enabled through the named policy. WATCH operators/targets are fixed by the shared domain contract; edge-case
tests should challenge semantics, not bypass typing with arbitrary payloads.
