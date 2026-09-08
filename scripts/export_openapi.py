from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'apps/api/src'))
from pipe4.app import create_app
from pipe4.config import Settings
from pipe4.container import build_memory_container
settings=Settings(policy_path=ROOT/'config/policies/pipe4-policy.v1.yaml',evidence_local_root=ROOT/'data/openapi-evidence',enable_dev_fixtures=False,jwt_hs256_secret='openapi-only-secret',internal_api_token='openapi-internal-token')
app=create_app(build_memory_container(settings=settings))
out=ROOT/'contracts/openapi/pipe4-v1.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(app.openapi(),indent=2,sort_keys=True)+'\n',encoding='utf-8');print(out)
