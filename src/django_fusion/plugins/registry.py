"""Plugin registry: mapping + recommendations + request detection.

The registry turns the static :mod:`django_fusion.plugins.catalog` into a
live, view-consumable service:

- :meth:`PluginRegistry.catalog` — every known plugin spec.
- :meth:`PluginRegistry.registered` / :meth:`PluginRegistry.available` —
  which plugins are wired into pluggy / importable in this environment.
- :meth:`PluginRegistry.recommend` — "I need capability X" → plugin specs.
- :meth:`PluginRegistry.detect` — "this request uses HTMX/fragments/SSE" →
  matched signals + recommended plugins.
- :meth:`PluginRegistry.summary` — a single serializable snapshot for views,
  templates and the debug-tools introspection dashboard.

Usage::

    from django_fusion.plugins import plugins

    plugins.recommend("htmx")          # → [PluginSpec(django_fusion.plugins.htmx)]
    plugins.detect(request)            # → {"signals": [...], "recommended": [...]}
    plugins.summary()                  # → dict for a view/dashboard
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from . import hookspecs
from .catalog import PluginSpec, get_catalog
from .manager import pm

#: Request signals the registry knows how to detect, keyed by the header
#: (or path prefix) that proves the runtime feature is in use.
_SIGNAL_HEADERS: dict[str, tuple[str, str]] = {
    "htmx-request": ("HX-Request", "true"),
    "fragment-request": ("HX-Target", None),  # any value proves a fragment swap
    "unpoly-request": ("X-Up-Target", None),
}
_SSE_ACCEPT = "text/event-stream"
_API_PATH_PREFIXES = ("/api/", "/apis/", "/fragment/")


class PluginRegistry:
    """Live registry mapping plugin packages → capabilities and signals."""

    def __init__(self) -> None:
        self._catalog: dict[str, PluginSpec] = {}
        self._lock = Lock()
        self._hook_specs_loaded = False
        self.rebuild_catalog()

    # ── Catalog ──────────────────────────────────────────────────────────
    def rebuild_catalog(self) -> None:
        """(Re)build the catalog from built-ins + hook-contributed specs."""
        with self._lock:
            self._catalog = get_catalog()
            self._hook_specs_loaded = False

    def _ensure_hook_specs(self) -> None:
        """Merge ``register_plugin_specs`` hook contributions once."""
        if self._hook_specs_loaded:
            return
        with self._lock:
            if self._hook_specs_loaded:
                return
            try:
                def _register(spec: PluginSpec) -> None:
                    if spec.name not in self._catalog:
                        self._catalog[spec.name] = spec
                    else:
                        # Hook wins on capability/signal metadata for the same name.
                        self._catalog[spec.name] = spec

                pm.hook.register_plugin_specs(register=_register)
            except Exception:  # pragma: no cover - defensive; hooks are optional
                pass
            self._hook_specs_loaded = True

    def catalog(self) -> list[PluginSpec]:
        """All known plugin specs, sorted by name."""
        self._ensure_hook_specs()
        return [self._catalog[name] for name in sorted(self._catalog)]

    def get(self, name: str) -> PluginSpec | None:
        """Return a spec by canonical module name."""
        self._ensure_hook_specs()
        return self._catalog.get(name)

    # ── Availability ─────────────────────────────────────────────────────
    @staticmethod
    def is_registered(name: str) -> bool:
        """True when *name* is registered with the pluggy manager."""
        try:
            return pm.get_plugin(name) is not None
        except Exception:
            return False

    @staticmethod
    def is_available(name: str) -> bool:
        """True when *name* imports cleanly (shipped + installed)."""
        try:
            importlib.import_module(name)
            return True
        except Exception:
            return False

    def registered(self) -> list[PluginSpec]:
        """Specs for plugins currently registered with pluggy."""
        self._ensure_hook_specs()
        return [spec for spec in self.catalog() if self.is_registered(spec.name)]

    def available(self) -> list[PluginSpec]:
        """Specs for plugins that are importable in this environment."""
        self._ensure_hook_specs()
        return [spec for spec in self.catalog() if self.is_available(spec.name)]

    # ── Capabilities & recommendations ───────────────────────────────────
    def capabilities(self) -> set[str]:
        """Union of every capability offered by the full catalog."""
        self._ensure_hook_specs()
        return {cap for spec in self.catalog() for cap in spec.capabilities}

    def recommend(self, capability: str) -> list[PluginSpec]:
        """Return the plugin specs that provide *capability* (best-effort).

        Prefers plugins that are already registered/available, then falls
        back to the full catalog so the result is still actionable.
        """
        self._ensure_hook_specs()
        matched = [spec for spec in self.catalog() if capability in spec.capabilities]
        return sorted(
            matched,
            key=lambda spec: (not self.is_available(spec.name), spec.name),
        )

    # ── Request detection ────────────────────────────────────────────────
    @staticmethod
    def _signals_for_request(request: Any) -> set[str]:
        """Extract the set of runtime signals from an HttpRequest."""
        signals: set[str] = set()
        headers = getattr(request, "headers", None)
        meta = getattr(request, "META", None) or {}
        path = getattr(request, "path", "") or ""

        if headers is None:  # RequestFactory/old-style tests fallback
            def _header(name: str) -> str | None:
                return meta.get(f"HTTP_{name.upper().replace('-', '_')}")

            headers = type("_H", (), {"get": lambda self, n, d=None: _header(n) or d})()

        for signal, (header, expected) in _SIGNAL_HEADERS.items():
            value = headers.get(header) if hasattr(headers, "get") else None
            if value is not None and (expected is None or str(value).lower() == expected):
                signals.add(signal)

        accept = (headers.get("Accept") if hasattr(headers, "get") else None) or ""
        if _SSE_ACCEPT in accept:
            signals.add("sse")

        if any(path.startswith(prefix) for prefix in _API_PATH_PREFIXES):
            signals.add("api-request")

        return signals

    def detect(self, request: Any) -> dict[str, Any]:
        """Detect runtime signals on *request* and recommend plugins.

        Returns a serializable snapshot::

            {
                "signals": ["htmx-request"],
                "matched": ["django_fusion.plugins.htmx"],
                "recommended": ["django_fusion.plugins.htmx"],
            }
        """
        self._ensure_hook_specs()
        signals = self._signals_for_request(request)

        matched: set[str] = set()
        for spec in self.catalog():
            if spec.signals & signals:
                matched.add(spec.name)

        recommended = sorted(
            matched,
            key=lambda name: (self.is_registered(name), self.is_available(name)),
            reverse=True,
        )
        return {
            "signals": sorted(signals),
            "matched": sorted(matched),
            "recommended": recommended,
        }

    # ── Serialization for views/dashboards ───────────────────────────────
    def summary(self) -> dict[str, Any]:
        """One serializable snapshot of the whole plugin layer."""
        self._ensure_hook_specs()
        specs = []
        for spec in self.catalog():
            available = self.is_available(spec.name)
            registered = self.is_registered(spec.name)
            specs.append(spec.to_dict(available=available, registered=registered))
        return {
            "total": len(specs),
            "registered": sum(1 for s in specs if s["registered"]),
            "available": sum(1 for s in specs if s["available"]),
            "capabilities": sorted(self.capabilities()),
            "plugins": specs,
        }


#: Process-wide singleton — mirrors ``components``/``cache`` patterns.
_registry: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    """Get or create the global plugin registry."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


plugins = get_plugin_registry()

__all__ = ["PluginRegistry", "PluginSpec", "get_plugin_registry", "plugins"]
