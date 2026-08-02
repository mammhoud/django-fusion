from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Type

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
#  Component settings singleton
# ═══════════════════════════════════════════════════════════════

_DEFAULT_COMPONENT_DIRS = ("components", "partials", "tags")


class DjangoComponentsSettings:
    """Minimal settings façade consumed by the component system."""

    def __init__(self) -> None:
        self._component_dir_names: tuple[str, ...] | None = None
        self._enable_block_attrs: bool | None = None
        self._add_asset_prefix: bool | None = None
        self.FUSION_RENDER_FIRST_DEFAULT = self._resolve_render_first_default()

    def get_component_directory_names(self) -> tuple[str, ...]:
        if self._component_dir_names is None:
            self._component_dir_names = self._resolve_component_dir_names()
        return self._component_dir_names

    def _resolve_component_dir_names(self) -> tuple[str, ...]:
        try:
            from django.conf import settings as django_settings

            raw = getattr(django_settings, "COMPONENTS_DIR_NAMES", None)
            if raw and isinstance(raw, (list, tuple)):
                return tuple(raw)
        except Exception:  # noqa: BLE001
            pass
        return _DEFAULT_COMPONENT_DIRS

    def _resolve_render_first_default(self) -> bool:
        try:
            from django.conf import settings as django_settings

            return bool(
                getattr(
                    django_settings,
                    "FUSION_RENDER_FIRST_DEFAULT",
                    getattr(django_settings, "COMPONENTS_FUSION_RENDER_FIRST_DEFAULT", False),
                )
            )
        except Exception:  # noqa: BLE001
            return False

    def should_add_asset_prefix(self) -> bool:
        if self._add_asset_prefix is None:
            self._add_asset_prefix = self._resolve_asset_prefix()
        return self._add_asset_prefix

    def _resolve_asset_prefix(self) -> bool:
        try:
            from django.conf import settings as django_settings

            return bool(getattr(django_settings, "COMPONENTS_ADD_ASSET_PREFIX", False))
        except Exception:  # noqa: BLE001
            return False

    @property
    def enable_block_attrs(self) -> bool:
        if self._enable_block_attrs is None:
            self._enable_block_attrs = self._resolve_enable_block_attrs()
        return self._enable_block_attrs

    # Backwards-compatible alias
    @property
    def ENABLE_BLOCK_ATTRS(self) -> bool:  # noqa: N802
        return self.enable_block_attrs

    def _resolve_enable_block_attrs(self) -> bool:
        try:
            from django.conf import settings as django_settings

            return bool(getattr(django_settings, "COMPONENTS_ENABLE_BLOCK_ATTRS", False))
        except Exception:  # noqa: BLE001
            return False

    def reset(self) -> None:
        self._component_dir_names = None
        self._enable_block_attrs = None
        self._add_asset_prefix = None
        self.FUSION_RENDER_FIRST_DEFAULT = self._resolve_render_first_default()


_settings = DjangoComponentsSettings()


def get_settings() -> DjangoComponentsSettings:
    """Return the shared settings singleton."""
    return _settings


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
    from django.utils.functional import SimpleLazyObject

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
