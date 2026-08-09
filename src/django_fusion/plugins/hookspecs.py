from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from pluggy import HookspecMarker

if TYPE_CHECKING:
    from ..staticfiles import Asset, AssetType
    from .catalog import PluginSpec

hookspec = HookspecMarker("django_fusion.comp")


@hookspec
def collect_component_assets(template_path: Path) -> Iterable[Asset]:
    """Collect all assets associated with a component.

    This hook is called for each component template to gather its associated static assets.
    Implementations should scan for and return any CSS, JavaScript or other static files
    that belong to the component and return a list/set/other iterable of `Asset` objects.
    """


@hookspec
def get_template_directories() -> list[Path]:
    """Return a list of all directories containing templates for a project.

    This hook allows plugins to provide additional template directories beyond the default
    Django template directories. Implementations should return a list of Path objects
    pointing to directories that contain Django templates.

    The template directories returned by this hook will be used by django-block to discover
    components and their associated templates.
    """


@hookspec
def pre_ready() -> None:
    """Called before django-block begins its internal setup.

    This hook runs at the start of django-block's initialization, before any internal
    components are configured or discovered. Plugins can use this hook to perform early
    configuration of:

    - Django settings
    - Template directories
    - Template builtins
    """


@hookspec
def ready() -> None:
    """Called after django-block application has completed its internal setup and is ready.

    This hook is called during Django's application ready phase, after django-block's own
    initialization is complete. Plugins can:

    - Access fully configured components
    - Register additional features that depend on django-block being ready
    - Perform cleanup or post-initialization tasks
    """


@hookspec
def register_asset_types(register_type: Callable[[AssetType], None]) -> None:
    """Register a new type of asset.

    This hook allows plugins to register additional asset types beyond the default CSS
    and JS types. Each asset type defines how static assets should be rendered in HTML,
    what file extension it uses, and what django-block asset templatetag it should be
    rendered with.
    """


@hookspec
def register_plugin_specs(register: Callable[["PluginSpec"], None]) -> None:
    """Declare a plugin package's capabilities to the fusion plugin registry.

    Implementations receive a ``register`` callable and should invoke it once
    per ``PluginSpec`` they provide (name, capabilities, signals). The specs
    feed the plugin catalog consumed by :mod:`django_fusion.plugins.registry`
    (recommendations, request detection and the introspection dashboard).

    Example::

        from django_fusion.plugins.catalog import PluginSpec
        from pluggy import HookimplMarker

        hookimpl = HookimplMarker("django_fusion.comp")

        @hookimpl
        def register_plugin_specs(register):
            register(PluginSpec(name=__name__, capabilities={"my-feature"}))
    """
