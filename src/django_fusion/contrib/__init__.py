"""Contrib — pluggable extensions for admin, caching, debugging, and privacy.

Sub-packages
------------
contrib.admin           Custom admin site class and Wagtail admin Wagtail hooks.
contrib.cache           Cache utility functions (key builders, invalidation helpers).
contrib.debug_tools     Dev-only diagnostics: autoreload, Sentry, Prometheus, error views.
contrib.email_config    Email backend configuration helpers.
contrib.enums           Shared choice enums used across contrib modules.
contrib.privacy         Privacy consent middleware and cookie policy helpers.
contrib.utils           Miscellaneous shared utility functions.
"""

import re
from functools import cached_property

# ── Safe direct imports (module-level, no submodule loading) ────────────────
from django_fusion.site import (
    DEFAULT,
    camel_case_to_underscore,
    list_path_components,
    strip_suffixes,
)

# ── Backward-compat aliases ─────────────────────────────────────────────────
ViewProp = cached_property


# ── Local utilities ─────────────────────────────────────────────────────────

def camel_case_to_title(name: str) -> str:
    """Convert CamelCase to Title Case (e.g. MyModel → My Model)."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1 \2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s1)


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
        import django_fusion.site

        val = getattr(django_fusion.site, name)
        globals()[name] = val
        return val

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
