"""Plugin catalog for django-fusion.

The catalog is the single source of truth for *what each plugin package
does*. It maps a plugin module to:

- ``capabilities`` — feature keywords the plugin provides (e.g. ``htmx``,
  ``fragments``, ``sse``, ``webpack``). Use these with
  :meth:`PluginRegistry.recommend` to discover the right plugin for a
  capability.
- ``signals`` — request-side markers the plugin understands (e.g. an
  ``HX-Request`` header for the HTMX plugin). The registry's
  :meth:`PluginRegistry.detect` scans an incoming ``HttpRequest`` for
  these and reports which plugins are relevant.

Plugins may extend the catalog through the ``register_plugin_specs``
hook (see :mod:`django_fusion.plugins.hookspecs`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Canonical core plugins that are auto-registered with the pluggy manager
# in ``django_fusion.plugins.manager``.
CORE_PLUGINS: tuple[str, ...] = (
    "django_fusion.config.staticfiles",
    "django_fusion.comp.loader.templates",
)


@dataclass(frozen=True, slots=True)
class PluginSpec:
    """Static description of one django-fusion plugin package."""

    name: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    description: str = ""
    signals: frozenset[str] = field(default_factory=frozenset)
    core: bool = False

    @property
    def short_name(self) -> str:
        """Last dotted segment — e.g. ``htmx`` for ``django_fusion.plugins.htmx``."""
        return self.name.rsplit(".", 1)[-1]

    def to_dict(self, *, available: bool = False, registered: bool = False) -> dict:
        """Serializable payload for views/JSON endpoints."""
        return {
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "capabilities": sorted(self.capabilities),
            "signals": sorted(self.signals),
            "core": self.core,
            "available": available,
            "registered": registered,
        }


#: Built-in catalog. ``core=True`` marks the plugins that the manager
#: registers with pluggy on import; the rest are shipped utility packages
#: that sites opt into (and that the recommender suggests enabling).
PLUGIN_CATALOG: dict[str, PluginSpec] = {
    "django_fusion.config.staticfiles": PluginSpec(
        name="django_fusion.config.staticfiles",
        capabilities=frozenset(
            {"staticfiles", "assets", "component-assets", "css", "js", "asset-pipeline"}
        ),
        description=(
            "Serves component static assets and registers the CSS/JS asset "
            "pipeline (AssetType collection) used by {% comp %} rendering."
        ),
        core=True,
    ),
    "django_fusion.comp.loader.templates": PluginSpec(
        name="django_fusion.comp.loader.templates",
        capabilities=frozenset(
            {"templates", "component-discovery", "loader", "template-usage"}
        ),
        description=(
            "Discovers component templates, tracks template→component usage, "
            "and feeds the component registry + render-history tracker."
        ),
        core=True,
    ),
    "django_fusion.plugins.htmx": PluginSpec(
        name="django_fusion.plugins.htmx",
        capabilities=frozenset({"htmx", "fragments", "sse", "ajax", "partial-render"}),
        signals=frozenset({"htmx-request", "fragment-request", "sse"}),
        description=(
            "HTMX request detection (HtmxDetails), fragment swap helpers, SSE "
            "push utilities and HTMX response helpers for dual-mode views."
        ),
    ),
    "django_fusion.plugins.unpoly": PluginSpec(
        name="django_fusion.plugins.unpoly",
        capabilities=frozenset({"unpoly", "progressive-enhancement", "pushstate"}),
        signals=frozenset({"unpoly-request"}),
        description=(
            "Unpoly progressive-enhancement support: request detection and "
            "adapter helpers for pages served with the Unpoly JS runtime."
        ),
    ),
    "django_fusion.plugins.apis": PluginSpec(
        name="django_fusion.plugins.apis",
        capabilities=frozenset({"api", "schemas", "serialization", "bolt"}),
        signals=frozenset({"api-request", "fragment-request"}),
        description=(
            "Typed API helpers: pydantic-style schema registry, model↔schema "
            "mapping and optional Rust-backed Bolt route generation."
        ),
    ),
    "django_fusion.plugins.webpack": PluginSpec(
        name="django_fusion.plugins.webpack",
        capabilities=frozenset({"webpack", "bundle-tracker", "assets"}),
        description=(
            "Webpack bundle-tracker compatibility so django-webpack-loader "
            "manifests resolve through the fusion asset pipeline."
        ),
    ),
    "django_fusion.plugins.debug_tools": PluginSpec(
        name="django_fusion.plugins.debug_tools",
        capabilities=frozenset(
            {"debugging", "introspection", "dev-tools", "monitoring", "profiling"}
        ),
        description=(
            "Development tooling: debug toolbar, Silk, livereload, Prometheus "
            "metrics, error views and the fusion introspection dashboard."
        ),
    ),
    "django_fusion.plugins.designer": PluginSpec(
        name="django_fusion.plugins.designer",
        core=True,
        description="Interactive designer: component catalog, Wagtail field suggestions, "
        "form/table scaffolds, website audits, and safe component previews.",
        capabilities={"designer", "component-catalog", "wagtail-field", "form-scaffold", "table-scaffold"},
        signals=frozenset({"designer_tools_call"}),
    ),
    "django_fusion.tasks": PluginSpec(
        name="django_fusion.tasks",
        core=True,
        description="Unified background-task API with broker-agnostic registration, "
        "Dramatiq/RQ/in-process backends, task logging, idempotency, and MCP-safe enqueue.",
        capabilities={"tasks", "background-jobs", "dramatiq", "async-email"},
        signals=frozenset({"task_enqueued", "task_completed", "task_failed"}),
    ),
    "django_fusion.plugins.robyn": PluginSpec(
        name="django_fusion.plugins.robyn",
        capabilities=frozenset({"robyn", "async-server", "health"}),
        description=(
            "Robyn async-server adapter that mounts fusion viewsets as Robyn "
            "routes with a /fusion/health endpoint."
        ),
    ),
}


def get_catalog() -> dict[str, PluginSpec]:
    """Return the full catalog (built-ins only — hook specs are merged by the registry)."""
    return dict(PLUGIN_CATALOG)
