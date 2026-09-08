# ADR 0010 — Uwaci Ownership Mapping

**Status:** Accepted for reference service v1.0

## Decision

Standalone reference entity/source/provenance stores are adapters only. UWACI integration maps to Identity, Presence, Locator, Knowledge, Core AI, Usage, and Notification ownership.

## Consequences

- The decision is explicit and testable.
- Any replacement must preserve Pipe 4 invariants and document migration/consumer impact.
- Host-project integration may substitute infrastructure only through the defined ports/contracts.
