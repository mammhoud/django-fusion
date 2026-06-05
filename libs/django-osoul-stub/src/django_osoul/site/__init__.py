"""Stub site module for django-osoul."""
from .enums import *  # noqa: F401, F403
from ._context_mixins import *  # noqa: F401, F403


class WagtailPageMixin:
    """Stub Wagtail page mixin."""
    pass


def __getattr__(name):
    """Return a stub module for any requested attribute."""
    import types
    fake_mod = types.ModuleType(f"django_osoul.site.{name}")
    fake_mod.__file__ = f"/stub/django_osoul/site/{name}.py"
    return fake_mod


__all__ = ["WagtailPageMixin", "enums", "_context_mixins"]
