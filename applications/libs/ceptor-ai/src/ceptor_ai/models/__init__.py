"""Compatibility package for legacy ``ceptor_ai.models`` imports."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from ceptor_ai.content.models import *  # noqa: F401,F403

_CONTENT_MODELS = Path(__file__).resolve().parent.parent / "content" / "models"
__path__ = [str(_CONTENT_MODELS)]

for _module_path in _CONTENT_MODELS.glob("*.py"):
    if _module_path.stem == "__init__":
        continue
    _name = _module_path.stem
    _module = importlib.import_module(f"ceptor_ai.content.models.{_name}")
    sys.modules.setdefault(f"{__name__}.{_name}", _module)
    setattr(sys.modules[__name__], _name, _module)
