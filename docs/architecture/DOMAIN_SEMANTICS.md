# Pipe 4 Domain Semantics

## Five state domains

`AVAILABLE`, `ACCESSIBLE`, `WORKING`, `TIME`, and `CHANGED` are the only core domains. New industries reuse these domains through entity/object identity, qualifiers, typed values, and policies.

## Separate axes

- Published lifecycle: CURRENT, DISPUTED, STALE, EXPIRED, REPLACED.
- Epistemic status: DECLARED, OBSERVED, SYSTEM_REPORTED, TRANSACTION_EVIDENCED, INFERRED, VERIFIED.
- Verification status: UNVERIFIED, PENDING, VERIFIED, FAILED, INCONCLUSIVE.
- Request/acquisition lifecycle is separate from published state.
- Access-request lifecycle is separate from physical state.

UNKNOWN is represented by absence of an eligible canonical state plus a resolution/request outcome and presentation. It is never materialized as a fake observation with invented timestamps/location.
