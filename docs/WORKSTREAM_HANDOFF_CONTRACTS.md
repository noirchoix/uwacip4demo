# Workstream Handoff Contracts

Parallel work is safe only when workstreams exchange stable interfaces rather than importing each other's implementation details.

## Ibrahim -> Victory / Ernest / RoboTech

Must stabilize first:

- `StateIdentity` shape and canonical key;
- `StateValue` tagged union;
- state/observation/access/WATCH enums;
- publication decision inputs/outputs;
- presentation status mapping.

Any breaking change requires Samuel review and coordinated updates to schemas/repository tests.

## Ernest -> Victory / RoboTech / Jacob

Must expose repository behavior through `CurrentStateRepository` (or a reviewed split of that protocol), not raw session queries from route code.

Critical semantics:

- request session owns transaction boundary;
- observation insert is idempotent where key supplied;
- state publication appends a version;
- current projection replacement is atomic;
- history is queryable by stable identity key;
- WATCH/access/acquisition reads are principal-scoped.

## Victory -> Jacob / mobile

Must freeze:

- route paths and methods;
- request/response Pydantic shapes;
- operation IDs;
- auth behavior;
- error codes/envelopes;
- audio multipart parameter names.

No endpoint is considered contract-stable until Jacob's contract test proves it.

## RoboTech -> Ernest / Victory

Nearby and WATCH logic must be deterministic functions/services that accept explicit inputs. Repository concerns stay behind ports.

Do not embed SQL in ranking policy or Notification calls in condition-evaluation functions.

## Jacob -> all

Contract/acceptance tests are integration constraints, not a separate cleanup phase. A test failure caused by a deliberate contract change requires the owner of the change to update the coordinated contract, not weaken the test.
