from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    ROOT / "backend_overlay/app/modules/current_state/domain/enums.py",
    ROOT / "backend_overlay/app/modules/current_state/domain/identity.py",
    ROOT / "backend_overlay/app/modules/current_state/domain/idempotency.py",
    ROOT / "backend_overlay/app/modules/current_state/schemas/contracts.py",
    ROOT / "backend_overlay/tests/unit/current_state/test_state_identity.py",
    ROOT / "workstreams/OWNERSHIP.yaml",
    ROOT / "contracts/endpoint_manifest.json",
    ROOT / "docs/ACCEPTANCE_TRACEABILITY.md",
    ROOT / "docs/SECURITY_TEST_MATRIX.md",
    ROOT / "docs/FEATURE_ORCHESTRATION_MAP.md",
    ROOT / "docs/SOURCE_OF_TRUTH_DECISION_RECORD.md",
    ROOT / "docs/IMPLEMENTATION_STATUS.md",
    ROOT / "docs/PR_CHECKLIST.md",
    ROOT / "backend_overlay/tests/unit/current_state/test_hardening.py",
    ROOT / "reference_tests/test_hardening.py",
    ROOT / "TEAM_ONBOARDING_RUNBOOK.md",
    ROOT / "workstreams/README.md",
    ROOT / "scripts/check_host_compatibility.py",
    ROOT / "scripts/check_mobile_contract.py",
    ROOT / "docs/diagrams/01_end_to_end_workflow.png",
    ROOT / "docs/diagrams/02_layered_architecture.png",
    ROOT / "docs/diagrams/03_workstreams_and_ownership.png",
]

FORBIDDEN_TOP_LEVEL_IMPORTS = {
    "redis",
    "celery",
    "boto3",
    "deepgram",
}
FORBIDDEN_GOOGLE_PROVIDER_PREFIXES = {
    "google.genai",
    "google.generativeai",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def validate_required_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        fail("Missing starter files: " + ", ".join(missing))


def validate_endpoint_manifest() -> None:
    payload = json.loads(
        (ROOT / "contracts/endpoint_manifest.json").read_text(encoding="utf-8")
    )
    routes = payload.get("pipe4")
    if not isinstance(routes, list) or len(routes) != 17:
        fail("Expected exactly 17 mobile-consumed Pipe 4 routes")
    normalized = [tuple(route) for route in routes]
    if len(set(normalized)) != len(normalized):
        fail("Duplicate routes found in endpoint manifest")


def module_name(node: ast.Import | ast.ImportFrom) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    return [node.module or ""]


def validate_no_forbidden_runtime_imports() -> None:
    module_root = ROOT / "backend_overlay/app/modules/current_state"
    violations: list[str] = []
    for path in module_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Import | ast.ImportFrom):
                continue
            for name in module_name(node):
                top = name.split(".", 1)[0]
                if top in FORBIDDEN_TOP_LEVEL_IMPORTS or any(
                    name == prefix or name.startswith(prefix + ".")
                    for prefix in FORBIDDEN_GOOGLE_PROVIDER_PREFIXES
                ):
                    violations.append(
                        f"{path.relative_to(ROOT)}:{getattr(node, 'lineno', '?')} -> {name}"
                    )
    if violations:
        fail("Forbidden provider/infrastructure imports:\n" + "\n".join(violations))


def validate_line_lengths() -> None:
    violations: list[str] = []
    roots = [
        ROOT / "backend_overlay/app/modules/current_state",
        ROOT / "backend_overlay/tests/unit/current_state",
        ROOT / "reference_tests",
        ROOT / "scripts",
    ]
    for base in roots:
        for path in base.rglob("*.py"):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if len(line) > 100:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{lineno} ({len(line)} chars)"
                    )
    if violations:
        fail("Python lines exceed host 100-char limit:\n" + "\n".join(violations))


def validate_no_generated_cache_files() -> None:
    bad: list[str] = []
    for path in ROOT.rglob("*"):
        if path.name in {"__pycache__", ".pytest_cache"} or path.suffix == ".pyc":
            bad.append(str(path.relative_to(ROOT)))
    if bad:
        fail("Generated cache files must not ship:\n" + "\n".join(bad[:20]))


def validate_team_lead() -> None:
    ownership = (ROOT / "workstreams/OWNERSHIP.yaml").read_text(encoding="utf-8")
    if "team_lead: Samuel" not in ownership:
        fail("Ownership file must identify Samuel as team lead")


def validate_mobile_patch_scope() -> None:
    patch = (ROOT / "patches/mobile-contract-backend-truth.patch").read_text(
        encoding="utf-8"
    )
    expected = {
        "src/features/pipe4/api/contracts.ts",
        "src/features/pipe4/api/pipe4Api.ts",
        "src/features/pipe4/api/witnessAudioUpload.ts",
    }
    missing = [path for path in sorted(expected) if path not in patch]
    if missing:
        fail("Mobile contract patch is missing expected files: " + ", ".join(missing))



def validate_hardening_contract() -> None:
    enums = (
        ROOT / "backend_overlay/app/modules/current_state/domain/enums.py"
    ).read_text(encoding="utf-8")
    repository = (
        ROOT / "backend_overlay/app/modules/current_state/ports/repository.py"
    ).read_text(encoding="utf-8")
    nearby = (
        ROOT / "backend_overlay/app/modules/current_state/domain/nearby.py"
    ).read_text(encoding="utf-8")
    access = (
        ROOT / "backend_overlay/app/modules/current_state/domain/access.py"
    ).read_text(encoding="utf-8")
    models = (
        ROOT / "backend_overlay/app/modules/current_state/models/models.py"
    ).read_text(encoding="utf-8")
    model_exports = (
        ROOT / "backend_overlay/app/modules/current_state/models/__init__.py"
    ).read_text(encoding="utf-8")
    schema_exports = (
        ROOT / "backend_overlay/app/modules/current_state/schemas/__init__.py"
    ).read_text(encoding="utf-8")
    mobile_patch = (
        ROOT / "patches/mobile-contract-backend-truth.patch"
    ).read_text(encoding="utf-8")

    required_markers = {
        "enum WatchOperator": "class WatchOperator",
        "enum AccessPermission": "class AccessPermission",
        "atomic publication": "publish_state_version",
        "NearbyRankingPolicy": "class NearbyRankingPolicy",
        "typed AccessScope": "class AccessScope",
        "approved access scope": "approved_scope",
        "scoped observation idempotency": "uq_current_state_observation_actor_operation_key",
        "idempotency request hash": "idempotency_request_hash",
        "mobile WATCH operator": "WatchOperator",
        "mobile access scope": "Pipe4AccessScope",
    }
    bodies = {
        "enum WatchOperator": enums,
        "enum AccessPermission": enums,
        "atomic publication": repository,
        "NearbyRankingPolicy": nearby,
        "typed AccessScope": access,
        "approved access scope": access,
        "scoped observation idempotency": models,
        "idempotency request hash": models,
        "mobile WATCH operator": mobile_patch,
        "mobile access scope": mobile_patch,
    }
    missing = [
        label for label, marker in required_markers.items() if marker not in bodies[label]
    ]
    if missing:
        fail("Hardening contract markers missing: " + ", ".join(missing))
    if "append_state_version" in repository or "replace_current_projection" in repository:
        fail("Repository boundary must expose atomic publication only")
    if "import *" in model_exports or "import *" in schema_exports:
        fail("Module exports must remain explicit; wildcard exports are not allowed")

def main() -> None:
    validate_required_files()
    validate_endpoint_manifest()
    validate_no_forbidden_runtime_imports()
    validate_line_lengths()
    validate_no_generated_cache_files()
    validate_team_lead()
    validate_mobile_patch_scope()
    validate_hardening_contract()
    print("starter structure: OK")
    print("mobile endpoint manifest: 17 routes")
    print("runtime import boundary: OK")
    print("python line length <= 100: OK")
    print("generated cache files: none")
    print("team lead: Samuel")
    print("hardening contract: OK")


if __name__ == "__main__":
    main()
