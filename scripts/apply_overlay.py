from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

PROTECTED = {"main", "dev"}


def branch(repo: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safely copy Pipe 4 starter overlay into uwaci-backend."
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"Not a Git repository: {repo}")
    current = branch(repo)
    if current in PROTECTED or not current:
        raise SystemExit(f"Refusing to modify protected/detached branch: {current or '<detached>'}")

    overlay = Path(__file__).resolve().parents[1] / "backend_overlay"
    conflicts: list[Path] = []
    planned: list[tuple[Path, Path]] = []
    for source in overlay.rglob("*"):
        if not source.is_file():
            continue
        if "__pycache__" in source.parts or source.suffix == ".pyc":
            continue
        rel = source.relative_to(overlay)
        target = repo / rel
        if target.exists():
            conflicts.append(rel)
        else:
            planned.append((source, target))

    if conflicts:
        print("Existing paths were not overwritten:")
        for rel in conflicts:
            print(f"  - {rel}")
        raise SystemExit("Review conflicts manually; this helper never overwrites existing files.")

    for source, target in planned:
        print(f"COPY {source.relative_to(overlay)}")
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    print(f"Planned {len(planned)} new files on branch {current!r}.")
    if args.dry_run:
        print("Dry run only; no files changed.")


if __name__ == "__main__":
    main()
