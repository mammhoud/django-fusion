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

# Canonical setting names (easy, flat) with legacy fallbacks so projects
# still configuring the old verbose names keep working unchanged.
_RENDER_FIRST_SETTING_NAMES = (
    "FUSION_RENDER_FIRST",
    "FUSION_RENDER_FIRST_DEFAULT",
    "COMPONENTS_FUSION_RENDER_FIRST_DEFAULT",
)

# Canonical string-mode setting, then the legacy bool names (see the
# FUSION_RENDER_FIRST → FUSION_RENDER_MODE rename).
_RENDER_MODE_SETTING_NAMES = ("FUSION_RENDER_MODE",) + _RENDER_FIRST_SETTING_NAMES
_RENDER_MODES = ("render", "data", "mixed")


def coerce_render_mode(value) -> str | None:
    """Normalise a setting value into ``render`` / ``data`` / ``mixed``.

    Accepts the canonical strings, plus boolean values and boolean-ish strings
    for the legacy ``FUSION_RENDER_FIRST`` shape (True → render, False → data).
    Returns ``None`` for values that do not resolve to a known mode.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return "render" if value else "data"
    text = str(value).strip().lower()
    if text in _RENDER_MODES:
        return text
    if text in ("true", "1", "yes", "on"):
        return "render"
    if text in ("false", "0", "no", "off"):
        return "data"
    return None


def resolve_render_mode_setting(default: str = "data") -> str:
    """Resolve the effective render mode from Django settings.

    Reads the canonical ``FUSION_RENDER_MODE`` string first (``render`` /
    ``data`` / ``mixed``), then the legacy bool names
    ``FUSION_RENDER_FIRST`` / ``FUSION_RENDER_FIRST_DEFAULT`` /
    ``COMPONENTS_FUSION_RENDER_FIRST_DEFAULT``, falling back to *default*.
    """
    try:
        from django.conf import settings as django_settings

        for name in _RENDER_MODE_SETTING_NAMES:
            try:
                value = getattr(django_settings, name, None)
            except Exception:  # noqa: BLE001
                value = None
            if value is not None:
                mode = coerce_render_mode(value)
                if mode is not None:
                    return mode
    except Exception:  # noqa: BLE001
        pass
    return default


def resolve_render_first_setting(default: bool = False) -> bool:
    """Resolve the effective render-first default from Django settings.

    Reads the canonical ``FUSION_RENDER_FIRST`` setting first, then the
    legacy ``FUSION_RENDER_FIRST_DEFAULT`` / ``COMPONENTS_FUSION_RENDER_FIRST_DEFAULT``
    names, falling back to *default* when nothing is configured.

    This is the deprecated boolean view of the mode; prefer
    :func:`resolve_render_mode_setting` for new code. ``render`` and ``mixed``
    (which serves HTML by default) map to True; only ``data`` maps to False.
    """
    return resolve_render_mode_setting(default="render" if default else "data") != "data"


class DjangoComponentsSettings:
    """Minimal settings façade consumed by the component system."""

    def __init__(self) -> None:
        self._component_dir_names: tuple[str, ...] | None = None
        self._enable_block_attrs: bool | None = None
        self._add_asset_prefix: bool | None = None
        self.render_first_default = self._resolve_render_first_default()
        self.render_mode = self._resolve_render_mode()

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
        return resolve_render_first_setting(default=False)

    def _resolve_render_mode(self) -> str:
        return resolve_render_mode_setting(default="data")

    # Backwards-compatible alias for the renamed attribute (writable, so
    # existing call sites that assign it keep working).
    @property
    def FUSION_RENDER_FIRST_DEFAULT(self) -> bool:  # noqa: N802
        return self.render_first_default

    @FUSION_RENDER_FIRST_DEFAULT.setter
    def FUSION_RENDER_FIRST_DEFAULT(self, value: bool) -> None:
        self.render_first_default = bool(value)

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
        self.render_first_default = self._resolve_render_first_default()
        self.render_mode = self._resolve_render_mode()


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
