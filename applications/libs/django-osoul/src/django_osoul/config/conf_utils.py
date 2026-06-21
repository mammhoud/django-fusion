from __future__ import annotations

from enum import Enum
from typing import Any, Type

from django.apps import apps as django_apps
from django.conf import settings  # noqa: F401
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject  # noqa: F401


class ImportStrategy(str, Enum):
    """Strategies for importing modules"""

    STANDARD = "standard"
    DJANGO = "django"
    LAZY = "lazy"
    CACHED = "cached"


def import_attribute(path: str, strategy: ImportStrategy = ImportStrategy.DJANGO) -> Any:
    """
    Import an attribute from a module path.
    """
    assert isinstance(path, str), "Path must be a string"

    if strategy == ImportStrategy.LAZY:
        return _lazy_import_attribute(path)
    elif strategy == ImportStrategy.CACHED:
        return _cached_import_attribute(path)
    else:
        return _standard_import_attribute(path)


def _standard_import_attribute(path: str) -> Any:
    """Standard import using importlib."""
    try:
        import importlib
    except ImportError:
        from django.utils import importlib

    pkg, attr = path.rsplit(".", 1)
    module = importlib.import_module(pkg)
    return getattr(module, attr)


def _lazy_import_attribute(path: str) -> Any:
    def _import():
        return _standard_import_attribute(path)

    return SimpleLazyObject(_import)


def _cached_import_attribute(path: str) -> Any:
    import hashlib

    from django.core.cache import cache

    cache_key = f"import_attribute_{hashlib.md5(path.encode()).hexdigest()}"
    cached = cache.get(cache_key)

    if cached is None:
        cached = _standard_import_attribute(path)
        cache.set(cache_key, cached, 3600)

    return cached


def import_model(model_path: str) -> Type:
    try:
        return django_apps.get_model(model_path)
    except ValueError:
        raise ImproperlyConfigured("Model path must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(f"Model '{model_path}' has not been installed or does not exist")


def import_form(form_path: str) -> Type:
    return import_attribute(form_path)


def import_adapter(adapter_path: str) -> Any:
    return import_attribute(adapter_path)
