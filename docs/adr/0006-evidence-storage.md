# ADR 0006 — Evidence Storage

**Status:** Accepted for reference service v1.0

## Decision

Store evidence binary objects outside relational state tables through EvidenceStorePort; persist opaque refs and content hashes.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
