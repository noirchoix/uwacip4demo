# Pipe 4 Acceptance & Edge-Case Traceability

This file is the release traceability index. It is intentionally explicit so CI can prove that every mandatory acceptance ID and every edge-case ID has a named implementation/test owner.

## Baseline acceptance gates

| ID | Requirement | Primary automated proof |
|---|---|---|
| AC-01 | Fresh Known State | `apps/api/tests/test_acceptance_baseline.py::test_ac01_*` |
| AC-02 | Missing State | `apps/api/tests/test_acceptance_baseline.py::test_ac02_*` |
| AC-03 | Successful Acquisition | `apps/api/tests/test_acceptance_baseline.py::test_ac03_*` |
| AC-04 | Complete Acquisition Failure | `apps/api/tests/test_acceptance_baseline.py::test_ac04_*` |
| AC-05 | Stale State | `apps/api/tests/test_acceptance_baseline.py::test_ac05_*` |
| AC-06 | Contradiction | `apps/api/tests/test_acceptance_baseline.py::test_ac06_*` |
| AC-07 | State Transition | `apps/api/tests/test_acceptance_baseline.py::test_ac07_*` |
| AC-08 | Offline Observation | `apps/api/tests/test_acceptance_baseline.py::test_ac08_*` |
| AC-09 | AI Boundary | `apps/api/tests/test_acceptance_baseline.py::test_ac09_*` |
| AC-10 | AI Outage | `apps/api/tests/test_acceptance_baseline.py::test_ac10_*` |
| AC-11 | Permission Boundary | `apps/api/tests/test_acceptance_baseline.py::test_ac11_*` |
| AC-12 | Cross-Pipe Query | `apps/api/tests/test_acceptance_baseline.py::test_ac12_*` |
| AC-13 | Cross-Pipe Event | `apps/api/tests/test_acceptance_baseline.py::test_ac13_*` |
| AC-14 | WATCH | `apps/api/tests/test_acceptance_baseline.py::test_ac14_*` |
| AC-15 | WATCH Aggregation | `apps/api/tests/test_acceptance_baseline.py::test_ac15_*` |
| AC-16 | Source Learning | `apps/api/tests/test_acceptance_baseline.py::test_ac16_*` |
| AC-17 | Freshness Learning Readiness | `apps/api/tests/test_acceptance_baseline.py::test_ac17_*` |
| AC-18 | Horizontal Demonstration | `apps/api/tests/test_acceptance_baseline.py::test_ac18_*` |
| AC-19 | Provenance | `apps/api/tests/test_acceptance_baseline.py::test_ac19_*` |
| AC-20 | Uncertainty Survival | `apps/api/tests/test_acceptance_baseline.py::test_ac20_*` |

## MVP Addendum gates

| ID | Requirement | Primary automated proof |
|---|---|---|
| ADD-AC-01 | Access request lifecycle | `apps/api/tests/test_acceptance_addendum.py::test_add_ac01_*` |
| ADD-AC-02 | Mixed-domain nearby discovery | `apps/api/tests/test_acceptance_addendum.py::test_add_ac02_*` |
| ADD-AC-03 | All Watches management | `apps/api/tests/test_acceptance_addendum.py::test_add_ac03_*` |
| ADD-AC-04 | Witness pseudonymization | `apps/api/tests/test_acceptance_addendum.py::test_add_ac04_*` |
| ADD-AC-05 | Natural-language witness report | `apps/api/tests/test_acceptance_addendum.py::test_add_ac05_*` |
| ADD-AC-06 | Location fallback | `apps/api/tests/test_acceptance_addendum.py::test_add_ac06_*` |
| ADD-AC-07 | None-of-these provisional reality | `apps/api/tests/test_acceptance_addendum.py::test_add_ac07_*` |
| ADD-AC-08 | Reported observation vs Uwaci current state | `apps/api/tests/test_acceptance_addendum.py::test_add_ac08_*` |
| ADD-AC-09 | Targeted nearby acquisition | `apps/api/tests/test_acceptance_addendum.py::test_add_ac09_*` |
| ADD-AC-10 | Universal current-state presentation | `apps/api/tests/test_acceptance_addendum.py::test_add_ac10_*` |

## Edge cases

| ID | Requirement | Primary proof / mechanism |
|---|---|---|
| EC-001 | Reality Changes During Acquisition | `test_edge_cases.py::test_ec_001_002_time_boundaries_and_no_false_precision` + AC-08/revalidate flow |
| EC-002 | State Expires During User Decision | `test_edge_cases.py::test_ec_001_002_time_boundaries_and_no_false_precision` + AC-08/revalidate flow |
| EC-003 | Owner and Witnesses Disagree | `apps/api/tests/test_edge_case_matrix.py::test_ec_003_*` |
| EC-004 | Owner Is Dishonest | `apps/api/tests/test_edge_case_matrix.py::test_ec_004_*` |
| EC-005 | Witness Is Dishonest | `apps/api/tests/test_edge_case_matrix.py::test_ec_005_*` |
| EC-006 | Coordinated Manipulation | `apps/api/tests/test_edge_case_matrix.py::test_ec_006_*` |
| EC-007 | Duplicate Evidence | `apps/api/tests/test_edge_case_matrix.py::test_ec_007_*` |
| EC-008 | Location Spoofing | `apps/api/tests/test_edge_case_matrix.py::test_ec_008_*` |
| EC-009 | No Location Permission | `test_edge_cases.py::test_ec_009_quantity_partial_truth_is_not_boolean` is unrelated; location fallback is proved by ADD-AC-06 and Observation location status tests |
| EC-010 | Observation Arrives Late | `apps/api/tests/test_edge_case_matrix.py::test_ec_010_*` |
| EC-011 | Device Clock Is Wrong | `apps/api/tests/test_edge_case_matrix.py::test_ec_011_*` |
| EC-012 | Source Disappears Mid-Acquisition | `apps/api/tests/test_edge_case_matrix.py::test_ec_012_*` |
| EC-013 | Every Source Fails | `apps/api/tests/test_edge_case_matrix.py::test_ec_013_*` |
| EC-014 | AI Provider Fails | `apps/api/tests/test_edge_case_matrix.py::test_ec_014_*` |
| EC-015 | AI Misinterprets Observation | `apps/api/tests/test_edge_case_matrix.py::test_ec_015_*` |
| EC-016 | AI Hallucinates Source | `apps/api/tests/test_edge_case_matrix.py::test_ec_016_*` |
| EC-017 | Different Locations, Different Truths | `apps/api/tests/test_edge_case_matrix.py::test_ec_017_*` |
| EC-018 | Different Variants, Different Truths | `apps/api/tests/test_edge_case_matrix.py::test_ec_018_*` |
| EC-019 | Partial Availability | `apps/api/tests/test_edge_case_matrix.py::test_ec_019_*` |
| EC-020 | Quantity Matters | `test_edge_cases.py::test_ec_020_quantity_cannot_exceed_capacity` + typed QuantityStateValue |
| EC-021 | Access Depends on User | `apps/api/tests/test_edge_case_matrix.py::test_ec_021_*` |
| EC-022 | Time Is an Estimate | `apps/api/tests/test_edge_case_matrix.py::test_ec_022_*` |
| EC-023 | Sudden Mass-State Change | `apps/api/tests/test_edge_case_matrix.py::test_ec_023_*` |
| EC-024 | Authoritative Upstream State Becomes Wrong | `apps/api/tests/test_edge_case_matrix.py::test_ec_024_*` |
| EC-025 | State Recovers | `apps/api/tests/test_edge_case_matrix.py::test_ec_025_*` |
| EC-026 | Rapid Oscillation | `apps/api/tests/test_edge_case_matrix.py::test_ec_026_*` |
| EC-027 | State Rarely Changes | `apps/api/tests/test_edge_case_matrix.py::test_ec_027_*` |
| EC-028 | Massive Demand Spike | `test_edge_cases.py::test_ec_028_029_watch_equivalence_deduplicates_work` + AC-02/AC-15 |
| EC-029 | Massive WATCH Demand | `test_edge_cases.py::test_ec_028_029_watch_equivalence_deduplicates_work` + AC-02/AC-15 |
| EC-030 | WATCH State Changes Before Notification | `apps/api/tests/test_edge_case_matrix.py::test_ec_030_*` |
| EC-031 | Reward Farming | `apps/api/tests/test_edge_case_matrix.py::test_ec_031_*` |
| EC-032 | Self-Created Reality Gaps | `apps/api/tests/test_edge_case_matrix.py::test_ec_032_*` |
| EC-033 | Unauthorized State Request | `apps/api/tests/test_edge_case_matrix.py::test_ec_033_*` |
| EC-034 | Permission Changes After Subscription | `apps/api/tests/test_edge_case_matrix.py::test_ec_034_*` |
| EC-035 | Deleted or Closed Entity | `test_edge_cases.py::test_ec_035_identity_collision_prevented_by_truth_qualifiers` (identity part) + entity activity behavior documented for UWACI adapter |
| EC-036 | Entity Identity Collision | `test_edge_cases.py::test_ec_036_quantity_query_context_does_not_change_identity` + stable entity_id identity tests |
| EC-037 | Cross-Pipe Race Condition | `apps/api/tests/test_edge_case_matrix.py::test_ec_037_*` |
| EC-038 | Transaction Contradicts Inventory | `apps/api/tests/test_edge_case_matrix.py::test_ec_038_*` |
| EC-039 | Sensor Malfunction | `apps/api/tests/test_edge_case_matrix.py::test_ec_039_*` |
| EC-040 | State Category Is Economically Unsustainable | `apps/api/tests/test_edge_case_matrix.py::test_ec_040_*` |

## Release rule

A release fails traceability if any ID from AC-01..20, ADD-AC-01..10, or EC-001..040 is absent from this document. Some long-horizon learning/economic edge cases are represented by readiness/configuration tests rather than claiming learned models already exist; the requirements themselves frame those as SHOULD/eventual behaviors.
