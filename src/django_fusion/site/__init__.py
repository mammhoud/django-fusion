"""Backward-compatibility shim for ``django_fusion.site``.

The ``django_fusion.site`` namespace was restructured; its contents now
live under ``django_fusion.ci``.  This package keeps old imports working
by lazily forwarding them to their new canonical locations.
"""
from __future__ import annotations

# Names that are lazily re-exported from django_fusion.ci.
_CI_NAMES = {
    "ComponentViews",
    "ModalComponent",
    "PageHandler",
    "PaginatedComponentView",
    "PaginatedListView",
}

# Utility names historically exposed at django_fusion.site top level.
# They are resolved lazily via __getattr__ to avoid importing
# django_fusion.site.utils (and therefore django_fusion.ci.utils) at
# import time.
_UTIL_NAMES = {
    "DEFAULT",
    "camel_case_to_underscore",
    "list_path_components",
    "strip_suffixes",
}


def __getattr__(name: str):
    """Lazily re-export public names from their new canonical location."""
    if name in _CI_NAMES:
        from django_fusion.ci.page_handler import (
            ComponentViews,
            ModalComponent,
            PageHandler,
            PaginatedComponentView,
            PaginatedListView,
        )
        return locals()[name]

    if name == "NotificationMixin":
        from django_fusion.ci.notifications import NotificationMixin
        return NotificationMixin

    if name == "HtmxDetails":
        from django_fusion.ci.plugins import HtmxDetails
        return HtmxDetails

    if name in _UTIL_NAMES:
        from django_fusion.site import utils as _utils
        return getattr(_utils, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ComponentViews",
    "DEFAULT",
    "HtmxDetails",
    "ModalComponent",
    "NotificationMixin",
    "PageHandler",
    "PaginatedComponentView",
    "PaginatedListView",
    "camel_case_to_underscore",
    "list_path_components",
    "strip_suffixes",
]
