"""
django_osoul.contrib — re-exports utilities from django_osoul.site
for backward compatibility.
"""
import re
from functools import cached_property

# Core utilities from django_osoul.site
from django_osoul.site import (  # noqa: F401
    DEFAULT,
    ComponentViews,
    NotificationMixin,
    PageHandler,
    camel_case_to_underscore,
    get_files_from_dirs,
    list_path_components,
    strip_suffixes,
    unique_ordered,
)
from django_osoul.site.utils import viewprop  # noqa: F401

# ViewProp — cached_property alias kept for backward compat; prefer viewprop
ViewProp = cached_property


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


__all__ = [
    "DEFAULT",
    "ComponentViews",
    "NotificationMixin",
    "PageHandler",
    "ViewProp",
    "viewprop",
    "camel_case_to_title",
    "camel_case_to_underscore",
    "first_not_default",
    "get_files_from_dirs",
    "get_object_data",
    "has_object_perm",
    "list_path_components",
    "strip_suffixes",
    "unique_ordered",
]
