from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from django.conf import settings

from django_fusion.contrib.utils import unique_ordered

# ------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------
COMPONENTS_SETTINGS_NAME = "COMPONENTS"
COMPONENTS_BUILTINS = "django_fusion.comp.templatetags.components"
COMPONENTS_BUILTINS_UI = "django_fusion.templatetags.ui_tags"
COMPONENTS_FINDER = "django_fusion.comp.configuration.staticfiles.BlockAssetFinder"


# ------------------------------------------------------------------
# ENUMS
# ------------------------------------------------------------------
class ImportStrategy(str, Enum):
    """Strategies for importing modules"""

    STANDARD = "standard"
    DJANGO = "django"
    LAZY = "lazy"
    CACHED = "cached"


# ------------------------------------------------------------------
# DJANGO BLOCK SETTINGS
# ------------------------------------------------------------------
def _default_debug() -> bool:
    return settings.DEBUG


def _default_not_debug() -> bool:
    return not settings.DEBUG


@dataclass
class DjangoComponentsSettings:
    """Django Block component framework settings"""

    COMPONENT_DIRS: list[Path | str] = field(default_factory=list)
    ENABLE_BLOCK_ATTRS: bool = False
    ADD_ASSET_PREFIX: bool | None = None
    COMPONENT_CACHE_TIMEOUT: int = 3600  # 1 hour
    ENABLE_HOT_RELOAD: bool = field(default_factory=_default_debug)
    MINIFY_COMPONENTS: bool = field(default_factory=_default_not_debug)
    DEFAULT_COMPONENT_THEME: str = "default"

    # Component registration
    AUTO_DISCOVER_COMPONENTS: bool = False

    # Asset settings
    ASSET_VERSIONING: bool = field(default_factory=_default_not_debug)
    ASSET_CACHE_BUSTING: bool = True
    BUNDLE_ASSETS: bool = field(default_factory=_default_not_debug)

    # Import settings
    IMPORT_STRATEGY: ImportStrategy = ImportStrategy.DJANGO
    ENABLE_LAZY_LOADING: bool = True
    CACHE_IMPORTS: bool = True

    def __getattribute__(self, __name: str) -> object:
        user_settings = getattr(settings, COMPONENTS_SETTINGS_NAME, {})
        return user_settings.get(__name, super().__getattribute__(__name))

    def get_component_directory_names(self):
        return unique_ordered([*self.COMPONENT_DIRS, "components"])

    def should_add_asset_prefix(self) -> bool:
        """Determine if the app label prefix should be added to asset URLs."""
        if self.ADD_ASSET_PREFIX is not None:
            return self.ADD_ASSET_PREFIX
        # Fall back to the DEBUG setting (add prefix in production)
        return not settings.DEBUG

    def get_component_cache_key(self, component_name: str) -> str:
        """Generate cache key for component."""
        return f"block_component_{component_name}_{self.DEFAULT_COMPONENT_THEME}"

    def get_import_strategy(self) -> ImportStrategy:
        """Get the import strategy to use."""
        return self.IMPORT_STRATEGY


_settings = DjangoComponentsSettings()
