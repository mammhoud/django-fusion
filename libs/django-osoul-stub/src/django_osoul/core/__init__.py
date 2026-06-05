"""Stub core module for django-osoul."""
from .models import *  # noqa: F401, F403


def __getattr__(name):
    """Return a stub module for any requested attribute."""
    import types
    fake_mod = types.ModuleType(f"django_osoul.core.{name}")
    fake_mod.__file__ = f"/stub/django_osoul/core/{name}.py"
    return fake_mod


__all__ = ["models"]
