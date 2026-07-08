"""
django_fusion.site — public exports (all imports are lazy to avoid circular deps).

This module provides the core site functionality for django-fusion including:
- Template context mixins for request processing
- Notification system for user notifications
- Page handling and component views
- HTMX pagination and response utilities
- View utilities and helpers

The module uses lazy imports to avoid circular dependency issues.

Classes:
    BaseTemplateContextMixin: Base mixin for template context processing.
    SiteContext: Site-wide context processor.
    FragmentHandlerMixin: Mixin for handling HTMX fragment requests.
    NotificationMixin: Mixin for adding notifications to views.
    UnifiedNotification: Unified notification system.
    PageHandler: Page rendering handler.
    ComponentViews: Base class for component-based views.
    HTMXPaginationMixin: Mixin for HTMX pagination support.
    HtmxDetails: HTMX request details container.
    HttpResponseStopPolling: Response to stop long polling.
    HttpResponseClientRedirect: Client-side redirect response.

Functions:
    viewprop: Property descriptor for lazy property evaluation.
    camel_case_to_underscore: Convert CamelCase to snake_case.
    list_path_components: Split URL prefix into path components.
    strip_suffixes: Remove known suffixes from class names.
    get_files_from_dirs: Find files matching pattern in directories.
    unique_ordered: Remove duplicates while preserving order.
"""
import re

__all__ = [
    "BaseTemplateContextMixin",
    "SiteContext",
    "FragmentHandlerMixin",
    "WagtailPageMixin",
    "NotificationMixin",
    "UnifiedNotification",
    "PageHandler",
    "ComponentViews",
    "HTMXPaginationMixin",
    "HtmxDetails",
    "HttpResponseStopPolling",
    "HttpResponseClientRedirect",
    "viewprop",
]

# Sentinel for "no value provided" — used in Viewset.filter_kwargs
DEFAULT = object()


def __getattr__(name: str):
    """Lazy import of all site exports to avoid circular imports."""
    _context_names = {"BaseTemplateContextMixin", "SiteContext", "FragmentHandlerMixin", "WagtailPageMixin"}
    _notification_names = {"NotificationMixin", "UnifiedNotification"}
    _page_handler_names = {"ComponentViews", "PageHandler"}
    _paginator_names = {"HTMXPaginationMixin"}
    _plugin_names = {"HtmxDetails"}
    _response_names = {"HttpResponseClientRedirect", "HttpResponseStopPolling"}
    _utils_names = {"viewprop"}

    if name in _context_names:
        from ._context_mixins import (
            BaseTemplateContextMixin,
            FragmentHandlerMixin,
            WagtailPageMixin,
        )
        globals()["BaseTemplateContextMixin"] = BaseTemplateContextMixin
        globals()["SiteContext"] = BaseTemplateContextMixin
        globals()["FragmentHandlerMixin"] = FragmentHandlerMixin
        globals()["WagtailPageMixin"] = WagtailPageMixin
        return globals()[name]
    if name in _notification_names:
        from .notifications import NotificationMixin, UnifiedNotification
        globals()["NotificationMixin"] = NotificationMixin
        globals()["UnifiedNotification"] = UnifiedNotification
        return globals()[name]
    if name in _page_handler_names:
        from .page_handler import ComponentViews, PageHandler
        globals()["ComponentViews"] = ComponentViews
        globals()["PageHandler"] = PageHandler
        return globals()[name]
    if name in _paginator_names:
        from .paginators import HTMXPaginationMixin
        globals()["HTMXPaginationMixin"] = HTMXPaginationMixin
        return globals()[name]
    if name in _plugin_names:
        from .plugins import HtmxDetails
        globals()["HtmxDetails"] = HtmxDetails
        return globals()[name]
    if name in _response_names:
        from .response import HttpResponseClientRedirect, HttpResponseStopPolling
        globals()["HttpResponseClientRedirect"] = HttpResponseClientRedirect
        globals()["HttpResponseStopPolling"] = HttpResponseStopPolling
        return globals()[name]
    if name in _utils_names:
        from .utils import viewprop
        globals()["viewprop"] = viewprop
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def camel_case_to_underscore(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def list_path_components(prefix: str) -> list[str]:
    """Split a URL prefix into its path components."""
    return [p for p in prefix.strip("/").split("/") if p]


def strip_suffixes(name: str, suffixes: list[str]) -> str:
    """Remove known suffixes from a class name."""
    for suffix in suffixes:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def get_files_from_dirs(dirs, pattern: str = "*"):
    """Yield (file_path, base_dir) for all files matching pattern in dirs."""
    from pathlib import Path

    for d in dirs:
        for p in Path(d).rglob(pattern):
            if p.is_file():
                yield p, Path(d)


def unique_ordered(items) -> list:
    """Return items with duplicates removed, preserving order."""
    return list(dict.fromkeys(items))
