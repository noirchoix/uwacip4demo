# Pipe 4 Security and Privacy Test Matrix

Pipe 4 handles location, witness evidence, access scope and current-state decisions. Security tests are part of feature completion, not a later audit.

| Area | Threat / failure | Required test | Owner |
|---|---|---|---|
| authentication | anonymous caller reaches protected route | missing/invalid bearer token rejected by host auth | Victory / Jacob |
| authorization | IDOR on entity/state/access/watch IDs | another principal cannot read/mutate unauthorized resources | Victory / Jacob |
| access scope | approved access grants broader read than requested | enforce exact requested read scope; deny escalation | Ibrahim / Jacob |
| access lifecycle | revoked/expired grant remains usable | authorization re-check reflects current lifecycle | Ibrahim / Jacob |
| witness privacy | public DTO exposes auth user, raw identity or precise private source | pseudonymized public source presentation only | Victory / Jacob |
| evidence logging | raw text/audio/transcript appears in logs or domain event payload | sanitizer/log-capture regression test | Victory / Jacob |
| event safety | forbidden keys (`token`, `audio`, `transcript`, `raw_text`, `content`, etc.) enter host `DomainEvent` | host sanitizer rejects unsafe payload | Victory / Jacob |
| provisional identity | provisional/private metadata leaks through public current state | response shaping excludes internal fields | Jacob |
| location | precise location returned when not required | data minimization / precision policy test | Victory / Jacob |
| idempotency | replayed witness submission duplicates evidence/state | same idempotency key is deterministic | Ernest / Jacob |
| state history | update mutates prior version | append-only repository test | Ernest / Ibrahim |
| concurrency | simultaneous publication corrupts current pointer | transactional concurrency test | Ernest |
| AI boundary | AI output publishes state without evidence/verification | service test proves interpretation is non-authoritative | Victory / Ibrahim |
| prompt/provider data | provider internals appear in mobile DTO | contract snapshot/schema test excludes them | Victory / Jacob |
| Nearby | caller uses radius/limit to exfiltrate unbounded data | bounds + permission filtering + pagination/limit test | RoboTech / Jacob |
| WATCH | permissions change after subscription but alert still leaks state | trigger evaluation re-checks authorization | RoboTech / Jacob |
| acquisition | targeted request reveals precise private location/identity | approximate/public-safe offer contract test | RoboTech / Jacob |

## Minimum feature gate

A PR touching authentication, authorization, public DTOs, witness data, location, WATCH or acquisition cannot be considered complete without the applicable negative/security test above.

## Testing boundary

Prefer real domain/service behavior and disposable persistence over mocks. When a test double is necessary, use a complete fake at a stable owner-module boundary and assert the behavior visible to the caller rather than merely asserting that the fake was called.
