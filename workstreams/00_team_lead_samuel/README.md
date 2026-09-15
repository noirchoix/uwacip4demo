# Samuel — Team Lead / Integration Authority

## Mission

Keep one coherent Pipe 4 architecture while parallel work lands safely in the existing UWACI backend.

## Own / approve

- current_state module boundary;
- API/mobile contract freeze;
- cross-module adapter decisions;
- migration ownership and dependency decisions;
- ADRs for PostGIS or future worker infrastructure;
- PR integration order;
- final acceptance evidence and CTO handoff.

## Daily integration questions

1. Did any workstream duplicate Identity, Knowledge, Notification, Core AI, Locator or Presence ownership?
2. Did any PR make AI output canonical truth?
3. Did any PR overwrite state history instead of appending a version?
4. Did any PR change a mobile shape without OpenAPI + mobile contract coordination?
5. Did any PR introduce Redis/Celery/PostGIS without a demonstrated host requirement and reviewed decision?

## Merge order

Recommended dependency order:

```text
Ibrahim domain kernel
      +
Ernest persistence skeleton
      |
Victory services/adapters/API
      |
Jacob contract + acceptance hardening
      |
RoboTech Nearby/WATCH edge cases
      |
full integration gate
```

Parallel PRs are fine, but shared interface changes require Samuel review before both branches drift.
