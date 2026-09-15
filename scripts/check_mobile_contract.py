from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


API_REL = Path("src/features/pipe4/api/pipe4Api.ts")
AUDIO_REL = Path("src/features/pipe4/api/witnessAudioUpload.ts")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check the current uwaci-mobile Pipe 4 API surface "
            "against the starter manifest."
        )
    )
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    root = Path(__file__).resolve().parents[1]

    api = repo / API_REL
    audio = repo / AUDIO_REL
    if not api.exists() or not audio.exists():
        raise SystemExit("Pipe 4 mobile API files were not found at the expected paths")

    api_text = api.read_text(encoding="utf-8")
    audio_text = audio.read_text(encoding="utf-8")
    manifest_path = root / "contracts/endpoint_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    missing: list[str] = []
    for method, route in manifest["pipe4"]:
        if "{" in route:
            # Dynamic mobile strings cannot match the manifest literally.
            # Check their stable path prefix instead.
            stable = route.split("{", 1)[0]
            if stable not in api_text and stable not in audio_text:
                missing.append(f"{method} {route}")
            continue
        if route == "/pipe4/witness/audio-reports":
            if route not in audio_text:
                missing.append(f"{method} {route}")
        elif route not in api_text:
            missing.append(f"{method} {route}")

    if missing:
        print("MOBILE CONTRACT CHECK: FAIL")
        for item in missing:
            print(f"  missing consumer route: {item}")
        return 1

    count = len(manifest["pipe4"])
    print(f"MOBILE CONTRACT CHECK: {count} manifest routes represented")

    patch = root / "patches/mobile-contract-backend-truth.patch"
    result = subprocess.run(
        ["git", "apply", "--check", str(patch)],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        print("backend-truth mobile patch: applies cleanly")
    else:
        combined = (result.stderr or result.stdout).strip()
        if re.search(r"patch does not apply|already exists", combined, re.I):
            print(
                "backend-truth mobile patch: review needed "
                "(mobile may already have changed)"
            )
        else:
            print("backend-truth mobile patch: check failed")
        if combined:
            print(combined)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
