# Pipe 4 Pull Request Checklist

Use this in addition to the repository pull-request template.

## Scope

- [ ] One workstream / coherent behavior set.
- [ ] No unrelated cleanup.
- [ ] No runtime code under `workstreams/`.
- [ ] Shared interface changes reviewed by Samuel before dependent branches diverge.

## TDD / behavior evidence

- [ ] New behavior had a failing test first.
- [ ] RED failed for the expected missing behavior, not an environment/typo error.
- [ ] Minimal implementation made the test pass.
- [ ] Refactor kept behavior green.
- [ ] Regression / neighboring suite run.
- [ ] Tests exercise real behavior; mocks/fakes are minimal and complete enough for the contract.

## Architecture

- [ ] API -> service -> domain/ports dependency direction preserved.
- [ ] No direct write to another module's tables.
- [ ] No provider SDK imported into `current_state`.
- [ ] Observation remains distinct from published state.
- [ ] Historical state is append-preserving.
- [ ] Nearby relevance is not used as truth confidence.

## API / mobile contract

- [ ] Request/response schema change documented.
- [ ] OpenAPI contract test updated.
- [ ] Canonical `{success, data, meta}` response envelope preserved.
- [ ] Mobile impact identified and coordinated if needed.
- [ ] Internal evidence/source identifiers are not exposed accidentally.

## Persistence

- [ ] Migration derives from the real latest `dev` head.
- [ ] Repository does not own transaction commit/rollback unless host convention explicitly requires it.
- [ ] Concurrency/idempotency cases tested where relevant.
- [ ] Index intent documented for high-frequency queries.

## Security / privacy

- [ ] Authentication path covered.
- [ ] Authorization/ownership/IDOR cases covered.
- [ ] Requested access scope cannot expand silently.
- [ ] Event payloads exclude raw witness/audio/transcript/secret material.
- [ ] Public DTOs are privacy-safe.

## Quality gate

- [ ] Ruff format check passes.
- [ ] Ruff lint passes.
- [ ] mypy passes.
- [ ] focused tests pass.
- [ ] full pytest suite passes.
- [ ] Alembic SQL sanity passes if persistence changed.
- [ ] security/dependency checks run per host CI.
- [ ] `git diff --check` passes.

## PR description

- [ ] Workstream owner named.
- [ ] Acceptance IDs named.
- [ ] RED failure reason recorded.
- [ ] Tests/commands recorded.
- [ ] API impact recorded.
- [ ] DB/migration impact recorded.
- [ ] security/privacy impact recorded.
- [ ] cross-module impact recorded.
- [ ] unresolved gaps stated explicitly.
