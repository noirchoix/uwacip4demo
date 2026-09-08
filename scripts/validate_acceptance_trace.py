from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
trace = (ROOT / 'docs' / 'acceptance' / 'TRACEABILITY.md').read_text(encoding='utf-8')
required = [
    *[f'AC-{i:02d}' for i in range(1, 21)],
    *[f'ADD-AC-{i:02d}' for i in range(1, 11)],
    *[f'EC-{i:03d}' for i in range(1, 41)],
]
missing = [item for item in required if item not in trace]
if missing:
    raise SystemExit(f'Missing acceptance trace IDs: {missing}')
print(f'Acceptance trace IDs present: {len(required)}/{len(required)}')
