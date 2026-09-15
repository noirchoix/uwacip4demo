# Pipe 4 Team Onboarding

Use this checklist before coding.

1. Clone `uwaci-backend`, switch to current `dev`, pull, and create one focused feature/test/fix branch.
2. Run `uv sync --locked --all-groups` in the backend.
3. Read `README.md`, `docs/ARCHITECTURE.md`, `workstreams/README.md`, and your assigned workstream README.
4. From this starter, run:

```bash
python scripts/validate_starter.py
python scripts/check_host_compatibility.py --repo /path/to/uwaci-backend
python scripts/apply_overlay.py --repo /path/to/uwaci-backend --dry-run
```

5. Review any conflicts. Do not overwrite current backend files blindly.
6. Apply the overlay only from a non-protected branch:

```bash
python scripts/apply_overlay.py --repo /path/to/uwaci-backend
```

7. Work only in normal production paths. `workstreams/` is guidance, not runtime code.
8. Start each behavior with a failing test, then RED → GREEN → REFACTOR.
9. Do not write another module's tables directly or import provider SDKs into `current_state`.
10. Before PR, run focused tests plus the full backend quality gate from `README.md` and complete `docs/PR_CHECKLIST.md`.

PRs target `dev`. Samuel reviews shared interface/integration decisions; repository maintainers retain merge authority.
