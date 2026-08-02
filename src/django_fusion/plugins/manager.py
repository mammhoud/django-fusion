from __future__ import annotations

import importlib
import logging
from contextlib import suppress

import pluggy

from . import hookspecs

logger = logging.getLogger(__name__)
pm = pluggy.PluginManager("django_fusion.comp")
pm.add_hookspecs(hookspecs)

pm.load_setuptools_entrypoints("django-block")

DEFAULT_PLUGINS: list[str] = [
    "django_fusion.config.staticfiles",
    "django_fusion.comp.loader.templates",
]

for plugin in DEFAULT_PLUGINS:
    try:
        with suppress(ModuleNotFoundError):
            mod = importlib.import_module(plugin)
            pm.register(mod, plugin)
    except ImportError as e:
        logger.error("Failed to load plugin '%s': %s — %s", plugin, type(e).__name__, e)
    except Exception as e:
        logger.error("Unexpected error loading plugin '%s': %s — %s", plugin, type(e).__name__, e)
