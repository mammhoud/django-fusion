"""Ensure projects/ is importable for configs tests (no Django needed)."""
import sys
from pathlib import Path

_PROJECTS_DIR = Path(__file__).resolve().parents[2] / "projects"
if str(_PROJECTS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROJECTS_DIR))
