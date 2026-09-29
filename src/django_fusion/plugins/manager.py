from __future__ import annotations

import importlib
import logging
from contextlib import suppress

import pluggy

from . import hookspecs
from .catalog import CORE_PLUGINS

logger = logging.getLogger(__name__)

#: Entry-point group for **third-party / separately distributed** plugins — the
#: third attach surface described in
#: ``docs/plans/structa-cloud/plugins/plugins-architecture.md`` §4.
#:
#: A distribution opts in by declaring, in its own ``pyproject.toml``::
#:
#:     [project.entry-points."django-block"]
#:     my_plugin = "my_package.plugin"
#:
#: ``load_setuptools_entrypoints`` below then imports and registers it under that
#: name. The group name is a **historical mismatch** with ``django_fusion``
#: (inherited from django-block): renaming it would break every published plugin,
#: so it is recorded here rather than quietly swapped. django-fusion itself ships
#: no members — the group exists for external distributions, and the framework's
#: own plugins attach through :data:`CORE_PLUGINS` instead.
ENTRYPOINT_GROUP = "django-block"

pm = pluggy.PluginManager("django_fusion.comp")
pm.add_hookspecs(hookspecs)

pm.load_setuptools_entrypoints(ENTRYPOINT_GROUP)

#: Plugins registered at import. Derived from the catalog so the list cannot
#: drift from ``PluginSpec.core`` (see :data:`CORE_PLUGINS`).
DEFAULT_PLUGINS: list[str] = list(CORE_PLUGINS)

for plugin in CORE_PLUGINS:
    try:
        with suppress(ModuleNotFoundError):
            mod = importlib.import_module(plugin)
            pm.register(mod, plugin)
    except ImportError as e:
        logger.error("Failed to load plugin '%s': %s — %s", plugin, type(e).__name__, e)
    except Exception as e:
        logger.error("Unexpected error loading plugin '%s': %s — %s", plugin, type(e).__name__, e)
