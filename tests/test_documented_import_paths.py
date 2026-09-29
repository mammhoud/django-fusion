"""Pins the canonical import paths advertised to consumers.

The package docstring, README, and `docs/` set all promise specific import
paths. Prose drifts silently -- a renamed module keeps every test green while
the documentation sends users to an ImportError. This test imports each
advertised path so a rename fails the build instead.

When you move a public symbol, update this list *and* the docs in the same
change.
"""

from __future__ import annotations

import importlib

import pytest

# (module, attribute or None)
DOCUMENTED_PATHS: list[tuple[str, str | None]] = [
    # Routing
    ("django_fusion.routes.core.base", "Viewset"),
    ("django_fusion.routes.core.base", "Route"),
    ("django_fusion.routes.core.base", "route"),
    ("django_fusion.routes.core.sites", "Module"),
    ("django_fusion.routes.core.sites", "Application"),
    ("django_fusion.routes.core.landing", "Landing"),
    ("django_fusion.routes.components.routable", "RoutableComponent"),
    ("django_fusion.routes.components.fragments", "FragmentComponent"),
    ("django_fusion.routes.http.detection", "FragmentDetector"),
    ("django_fusion.routes.rendering.decorators", "fusion_view"),
    ("django_fusion.routes.rendering.render_mode", "resolve_render_mode"),
    ("django_fusion.routes.pages.handler", None),
    # Component system
    ("django_fusion.comp._init", "components"),
    ("django_fusion.comp.registry", "register_include_paths"),
    ("django_fusion.comp.cache", None),
    ("django_fusion.comp.loader", None),
    ("django_fusion.comp.tags.components", None),
    # Fragments
    ("django_fusion.fragments.forms", "FormMixin"),
    ("django_fusion.fragments.tables", "TableMixin"),
    ("django_fusion.fragments.analyzer.scanner", "scan"),
    # Not listed: ``django_fusion.fragments.viewsets`` defines Wagtail page
    # types, so importing it requires Wagtail in INSTALLED_APPS. This suite
    # deliberately runs without Wagtail installed as an app, so the import
    # raises Django's "doesn't declare an explicit app_label" RuntimeError.
    # It is exercised by the consuming Wagtail projects instead.
    # Core
    ("django_fusion.core.health", "HealthCheckView"),
    ("django_fusion.core.middlewares", None),
    ("django_fusion.core.context", None),
    ("django_fusion.core.rendering", None),
    ("django_fusion.core.encoder", None),
    # Config
    ("django_fusion.config.conf", "resolve_render_mode_setting"),
    ("django_fusion.config.loader", None),
    ("django_fusion.config.manifest", None),
    # Models / services
    ("django_fusion.models.base", "BaseModel"),
    ("django_fusion.models.mixins", "SoftDeleteModel"),
    ("django_fusion.models.auth", "Role"),
    ("django_fusion.models.email", "EmailTemplate"),
    ("django_fusion.models.datatoken", "DataToken"),
    ("django_fusion.models.cache_storage", "CachingStorage"),
    ("django_fusion.services", "BaseService"),
    ("django_fusion.services", "TokenService"),
    ("django_fusion.services.base", "ModelService"),
    ("django_fusion.services.jobs", "dispatch_job"),
    ("django_fusion.services.token", "TokenService"),
    ("django_fusion.services.crud", None),
    # Layer packages
    ("django_fusion.tasks", None),
    ("django_fusion.site", None),
    ("django_fusion.builder", None),
    ("django_fusion.template_fields", None),
    ("django_fusion.contrib", None),
]


@pytest.mark.parametrize(("module_name", "attribute"), DOCUMENTED_PATHS)
def test_documented_import_path_resolves(module_name: str, attribute: str | None):
    module = importlib.import_module(module_name)
    if attribute is not None:
        assert hasattr(module, attribute), f"{module_name} lost {attribute!r}"


def test_assets_urls_are_importable():
    """`from django_fusion.core.assets import urls` is the documented mount."""
    from django_fusion.core.assets import urls

    assert urls is not None


def test_optional_integrations_are_not_required_by_a_base_install():
    """Optional extras must not be pulled in by importing the base package.

    ``django_fusion.mcp`` and ``django_fusion.plugins.apis`` need the ``bolt``
    extra. They are allowed to fail on a base install -- but that failure must be
    an ImportError naming the missing dependency, never a hard import of the
    base package itself.
    """
    import django_fusion

    assert django_fusion.__version__
