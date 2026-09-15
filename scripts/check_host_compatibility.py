from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_PATHS = (
    "pyproject.toml",
    "app/main.py",
    "app/api/dependencies.py",
    "app/shared/schemas/response.py",
    "app/platform/database/base.py",
    "app/modules/identity",
    "app/modules/knowledge",
    "app/modules/core_ai",
    "app/modules/notification",
    "migrations/versions",
    "tests",
)

EXPECTED_PYPROJECT_MARKERS = (
    'name = "uwaci-backend"',
    'requires-python = ">=3.12"',
    'line-length = 100',
    'strict = true',
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether a uwaci-backend checkout still matches the starter assumptions."
    )
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()

    failures: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (repo / rel).exists():
            failures.append(f"missing required host path: {rel}")

    pyproject = repo / "pyproject.toml"
    if pyproject.exists():
        body = text(pyproject)
        for marker in EXPECTED_PYPROJECT_MARKERS:
            if marker not in body:
                warnings.append(f"host pyproject changed expected marker: {marker}")

    response = repo / "app/shared/schemas/response.py"
    if response.exists():
        body = text(response)
        for symbol in ("class ResponseMeta", "class SuccessResponse"):
            if symbol not in body:
                failures.append(f"host response contract missing {symbol}")

    deps = repo / "app/api/dependencies.py"
    if deps.exists() and "RequestID" not in text(deps):
        warnings.append("RequestID dependency was not found where the starter expects it")

    identity_models = repo / "app/modules/identity/models/models.py"
    if identity_models.exists() and '__tablename__ = "user_profiles"' not in text(identity_models):
        warnings.append("identity user_profiles table name changed; review Pipe 4 foreign keys")

    knowledge_models = repo / "app/modules/knowledge/models/models.py"
    if knowledge_models.exists():
        body = text(knowledge_models)
        if "ProvenanceAttachment" not in body:
            warnings.append(
                "Knowledge provenance attachment model changed; "
                "re-check observation mapping"
            )

    core_ai_models = repo / "app/modules/core_ai/models/models.py"
    if core_ai_models.exists():
        body = text(core_ai_models)
        markers = ("user_id", "operation", "idempotency_key", "request_hash")
        if not all(marker in body for marker in markers):
            warnings.append(
                "Core AI idempotency shape changed; review Pipe 4 scoped idempotency contract"
            )

    migrations = repo / "migrations/versions"
    if migrations.exists():
        revisions = sorted(path.name for path in migrations.glob("*.py"))
        if not revisions:
            failures.append("no Alembic revisions found")
        else:
            print(f"migration files: {len(revisions)} (latest filename: {revisions[-1]})")

    app_main = repo / "app/main.py"
    if app_main.exists():
        router_calls = len(re.findall(r"include_router", text(app_main)))
        print(f"app.main include_router references: {router_calls}")

    if failures:
        print("HOST COMPATIBILITY: FAIL")
        for item in failures:
            print(f"  ERROR: {item}")
        for item in warnings:
            print(f"  WARN:  {item}")
        return 1

    print("HOST COMPATIBILITY: BASELINE MATCH")
    for item in warnings:
        print(f"  WARN: {item}")
    if warnings:
        print(
            "Review warnings before applying the starter; "
            "do not patch unrelated host code blindly."
        )
    else:
        print("No structural drift detected in the checked assumptions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
