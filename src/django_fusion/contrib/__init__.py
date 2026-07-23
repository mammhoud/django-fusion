"""Contrib — pluggable extensions for admin, caching, debugging, and privacy.

Sub-packages
------------
contrib.admin           Custom admin site class and Wagtail admin hooks.
contrib.cache           Cache utility functions.
contrib.debug_tools     Dev-only diagnostics.
contrib.email_config    Email backend helpers.
contrib.enums           Shared choice enums.
contrib.privacy         Privacy consent middleware and cookie policy helpers.
contrib.utils           Miscellaneous shared utility functions.
"""

from __future__ import annotations

import re
from functools import cached_property

# ── Backward-compat aliases ─────────────────────────────────────────────────
ViewProp = cached_property


# ── Utility functions (re-exported from django_fusion.site.interface) ──────────────────

def camel_case_to_underscore(name: str) -> str:
    """Convert CamelCase to underscore_case.

    Examples::

        >>> camel_case_to_underscore("MyClassName")
        'my_class_name'
    """
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"_\2", s1).lower()


def list_path_components(path: str) -> list[str]:
    """Split a dotted / URL-style path into its components.

    Examples::

        >>> list_path_components("foo/bar/baz")
        ['foo', 'bar', 'baz']
        >>> list_path_components("foo.bar.baz")
        ['foo', 'bar', 'baz']
    """
    return [part for part in re.split(r"[./]", path) if part]


def strip_suffixes(name: str, suffixes: list[str]) -> str:
    """Remove any of the given suffixes from ``name``.

    Examples::

        >>> strip_suffixes("MyListView", ["View"])
        'MyList'
    """
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name


def camel_case_to_title(name: str) -> str:
    """Convert CamelCase to Title Case (e.g. MyModel → My Model)."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r" \2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r" \2", s1)


# ── Sentinel ────────────────────────────────────────────────────────────────
class _DEFAULT:
    """Sentinel indicating "use the default value"."""

    def __repr__(self) -> str:
        return "<DEFAULT>"


DEFAULT = _DEFAULT()


def first_not_default(*values, default=None):
    """Return the first value that is not the DEFAULT sentinel."""
    for v in values:
        if v is not DEFAULT:
            return v
    return default


def has_object_perm(user, action: str, model, obj=None) -> bool:
    """Check if user has a Django model permission for the given action.

    Args:
        user: Django user instance.
        action: One of 'view', 'add', 'change', 'delete'.
        model: Django model class.
        obj: Optional model instance for object-level permission check.

    Returns:
        True if the user has the permission, False otherwise.
    """
    app_label = model._meta.app_label
    model_name = model._meta.model_name
    perm = f"{app_label}.{action}_{model_name}"
    if obj is not None:
        return user.has_perm(perm, obj)
    return user.has_perm(perm)


def get_object_data(obj) -> dict:
    """Return a dict of field name → value for a model instance."""
    if obj is None:
        return {}
    return {
        field.name: getattr(obj, field.name, None)
        for field in obj._meta.get_fields()
        if hasattr(field, "name")
    }


# ── Lazy class re-exports (avoid circular imports during init) ──────────────
def __getattr__(name: str):
    _lazy_site_classes = {"ComponentViews", "NotificationMixin", "PageHandler"}

    if name in _lazy_site_classes:
        if name == "NotificationMixin":
            from django_fusion.site.interface.notifications import NotificationMixin
            return NotificationMixin
        elif name == "ComponentViews":
            from django_fusion.site.interface.page_handler import ComponentViews
            return ComponentViews
        elif name == "PageHandler":
            from django_fusion.site.interface.page_handler import PageHandler
            return PageHandler

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ── Public API ──────────────────────────────────────────────────────────────

__all__ = [
    "DEFAULT",
    "ViewProp",
    "camel_case_to_title",
    "camel_case_to_underscore",
    "first_not_default",
    "get_object_data",
    "has_object_perm",
    "list_path_components",
    "strip_suffixes",
    # Lazy-imported classes (available at runtime, not during module init):
    "ComponentViews",
    "NotificationMixin",
    "PageHandler",
]
