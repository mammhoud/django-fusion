from __future__ import annotations

from typing import Any

from .catalog import PluginSpec
from .manager import pm
from .registry import PluginRegistry, get_plugin_registry, plugins

__all__ = [
    "PluginSpec",
    "PluginRegistry",
    "pm",
    "plugins",
    "tracker",
    "FusionTracker",
    "get_plugin_registry",
    "get_tracker",
]


def __getattr__(name: str) -> Any:
    """Lazily expose the tracker (it imports ``comp._init`` which imports us)."""
    if name in {"tracker", "FusionTracker", "get_tracker"}:
        from . import tracker as _tracker_mod

        return getattr(_tracker_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
