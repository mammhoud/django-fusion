"""View-consumable tracker for fusion component usage.

A thin service layer over the component registry's render history,
the template→component usage map and the Redis component cache — so
views, templates and the introspection dashboard all read from one API.

Usage::

    from django_fusion.plugins.tracker import tracker

    tracker.record("product_card", page_path=request.path)
    history = tracker.get_render_history(limit=20)
    usage = tracker.usage()
    snapshot = tracker.stats()
"""

from __future__ import annotations

from typing import Any

# NOTE: ``django_fusion.comp._init`` is imported lazily on first use. The
# plugins package is itself first imported from inside ``comp/_init.py``,
# so an eager import here would hit a partially-initialized module.
_CACHE: dict[str, Any] = {}


def _components() -> Any:
    """Lazily import + memoize the component registry internals."""
    if "registry" not in _CACHE:
        from django_fusion.comp._init import ComponentRenderMetadata, components

        _CACHE["registry"] = (ComponentRenderMetadata, components)
    return _CACHE["registry"]


class FusionTracker:
    """Records + reports component/plugin usage for views and dashboards."""

    # ── Recording ────────────────────────────────────────────────────────
    def record(self, component_name: str, *, page_path: str | None = None) -> None:
        """Record one component render (in-memory + Redis when available)."""
        metadata_cls, components = _components()
        components.record_render(
            metadata_cls(name=component_name, page_path=page_path)
        )

    # ── History ──────────────────────────────────────────────────────────
    def get_render_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Recent render events as plain dicts (newest first)."""
        _, components = _components()
        events = components.get_render_history()
        recent = list(events)[-limit:]
        return [
            {
                "name": event.name,
                "page_path": event.page_path,
                "fragment_name": event.fragment_name,
                "props": dict(event.props),
            }
            for event in reversed(recent)
        ]

    # ── Usage map ────────────────────────────────────────────────────────
    def usage(self) -> dict[str, Any]:
        """Component→templates and template→components usage maps."""
        _, components = _components()
        component_usage: dict[str, list[str]] = {}
        for name, paths in components._component_usage.items():
            component_usage[name] = sorted(str(p) for p in paths)

        template_usage: dict[str, list[str]] = {}
        for path, names in components._template_usage.items():
            template_usage[str(path)] = sorted(names)

        return {
            "components": component_usage,
            "templates": template_usage,
            "component_count": len(component_usage),
            "template_count": len(template_usage),
        }

    # ── Combined snapshot ────────────────────────────────────────────────
    def stats(self) -> dict[str, Any]:
        """Plugins + components + cache in one serializable snapshot."""
        from .registry import plugins

        _, components = _components()
        cache_stats: dict[str, Any] = {}
        try:
            from django_fusion.comp.cache import get_component_map_cache

            cache_stats = get_component_map_cache().get_stats()
        except Exception:
            cache_stats = {"error": "cache unavailable"}

        usage = self.usage()
        history = self.get_render_history(limit=50)
        return {
            "plugins": plugins.summary(),
            "components": {
                "registered": len(components._components),
                "usage": usage,
            },
            "render_history": history,
            "render_count": len(history),
            "cache": cache_stats,
        }


#: Process-wide singleton.
_tracker: FusionTracker | None = None


def get_tracker() -> FusionTracker:
    """Get or create the global tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = FusionTracker()
    return _tracker


tracker = get_tracker()

__all__ = ["FusionTracker", "get_tracker", "tracker"]
