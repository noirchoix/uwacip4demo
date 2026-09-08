from __future__ import annotations
import json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];committed=ROOT/'contracts/openapi/pipe4-v1.json'
if not committed.exists(): raise SystemExit('Committed OpenAPI contract is missing. Run scripts/export_openapi.py.')
before=committed.read_text(encoding='utf-8');subprocess.run([sys.executable,str(ROOT/'scripts/export_openapi.py')],check=True);after=committed.read_text(encoding='utf-8')
if before!=after: raise SystemExit('OpenAPI contract drift detected. Review and commit the intentional schema change.')
print('OpenAPI contract is stable.')
