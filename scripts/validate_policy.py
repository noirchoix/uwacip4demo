from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'apps/api/src'))
from pipe4.domain.policies.config import load_policy_bundle
bundle=load_policy_bundle(ROOT/'config/policies/pipe4-policy.v1.yaml');print(bundle.version,bundle.content_hash,[s.value for s in bundle.state_types])
