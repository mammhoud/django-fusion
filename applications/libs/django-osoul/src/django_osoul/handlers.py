"""Backward-compatible imports for legacy django_osoul.handlers users."""

from __future__ import annotations

import importlib
import sys

from django_osoul.middlewares.error_tracker import ErrorTrackerMiddleware

_core = importlib.import_module("django_osoul.core.handlers.core")
_tagging = importlib.import_module("django_osoul.core.handlers.tagging")
sys.modules.setdefault(__name__ + ".core", _core)
sys.modules.setdefault(__name__ + ".tagging", _tagging)
DynamicComponentRenderer = _core.DynamicComponentRenderer

__all__ = ["DynamicComponentRenderer", "ErrorTrackerMiddleware"]
