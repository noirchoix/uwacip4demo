import sys
from pathlib import Path

OVERLAY = Path(__file__).resolve().parents[1] / "backend_overlay"
sys.path.insert(0, str(OVERLAY))
