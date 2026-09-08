# HANDOFF — UWACI Pipe 4 Production Reference v1.0

## Artifacts

The release is distributed as:

- `uwaci-pipe4-production-reference-v1.0.zip`
- `uwaci-pipe4-uwaci-mobile-integration-v1.0.patch`
- `uwaci-pipe4-uwaci-mobile-integration-v1.0-overlay.zip`
- `uwaci-pipe4-production-v1.0-SHA256SUMS.txt`

## Standalone startup

```bash
unzip uwaci-pipe4-production-reference-v1.0.zip
cd uwaci-pipe4-production-reference-v1.0
cp .env.example .env
docker compose up --build
```

Expected development endpoints:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API health: `http://localhost:8000/api/v1/health/live`
- API docs in development: `http://localhost:8000/docs`

## Backend local validation

```bash
cd apps/api
python -m venv .venv
# activate the environment
pip install -e ".[dev]"
python -m compileall -q src
pytest -q
ruff check .
mypy src
pip-audit
```

Validate policy and contract from the repository root:

```bash
python scripts/validate_policy.py
python scripts/validate_acceptance_trace.py
python scripts/export_openapi.py
python scripts/check_openapi_drift.py
```

## Web validation

```bash
cd apps/web
npm install
npm run check
npm run test
npm run build
```

## Mobile integration — preferred Git patch

From a clean UWACI mobile checkout at commit
`4c8951880cc50bfe2ccdb4b14e1b63acf1b0f375`:

```bash
git apply --check ../uwaci-pipe4-uwaci-mobile-integration-v1.0.patch
git apply ../uwaci-pipe4-uwaci-mobile-integration-v1.0.patch
npx expo install expo-location
npm run validate
```

The released patch itself has already passed `git apply --check` and a disposable actual apply against that exact commit.

## Mobile integration — overlay alternative

Unzip `uwaci-pipe4-uwaci-mobile-integration-v1.0-overlay.zip` and copy the contained overlay over the mobile repository root, then run:

```bash
npx expo install expo-location
npm run validate
```

## Engineering ownership

The standalone service intentionally owns reference entities/source profiles only for independent operation. During real UWACI backend integration:

- Identity replaces standalone authorization authority.
- Presence/approved entity owner replaces reference-entity canonical ownership.
- Locator replaces canonical location ownership.
- Knowledge replaces standalone provenance/source-trust authority.
- Core AI replaces the standalone AI gateway adapter.
- Usage replaces the standalone usage policy.
- Notification owns notification delivery.
- only approved Pipe 4 current-state/resolution persistence remains locally owned.

Do not copy standalone adapter tables into the UWACI backend merely because they exist in the reference service.

## Improvement rule

A replacement implementation should identify:

1. the current problem;
2. the invariant being protected;
3. the proposed mechanism;
4. why it is simpler/safer/faster;
5. trade-offs;
6. tests proving behavioral equivalence;
7. tests proving the improvement;
8. migration/integration impact.

“Better” must be demonstrated rather than asserted.
