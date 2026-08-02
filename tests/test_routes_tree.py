"""Regression tests for the physical django-fusion routes tree."""

from importlib import import_module
from pathlib import Path


def test_old_dynaconf_loader_file_is_removed():
    """The old loader path is absent; no compatibility shim is retained."""
    old_loader = (
        Path(__file__).parents[1]
        / "src"
        / "django_fusion"
        / "config"
        / "dynaconf_loader.py"
    )

    assert not old_loader.exists()


def test_legacy_webpack_assets_package_is_removed():
    """Asset endpoints have one canonical package and no forwarding shim."""
    legacy_assets = (
        Path(__file__).parents[1]
        / "src"
        / "django_fusion"
        / "plugins"
        / "webpack"
        / "assets"
    )

    assert not legacy_assets.exists()


def test_dynaconf_loader_uses_canonical_config_module():
    """The Dynaconf implementation is importable from config.loader."""
    loader = import_module("django_fusion.config.loader")

    assert loader.DynaconfSettings.__module__ == "django_fusion.config.loader"
    assert loader.ModelsRegistry.__module__ == "django_fusion.config.loader"
    assert loader.TemplateRegistry.__module__ == "django_fusion.config.loader"
    assert loader.load_dynaconf_settings.__module__ == "django_fusion.config.loader"


def test_route_implementations_live_in_canonical_subpackages():
    """Every moved implementation remains importable from its concrete module."""
    modules = (
        "django_fusion.routes.core.base",
        "django_fusion.routes.core.sites",
        "django_fusion.routes.core.converters",
        "django_fusion.routes.components.routable",
        "django_fusion.routes.components.fragments",
        "django_fusion.routes.components.dual_mode",
        "django_fusion.routes.models.base",
        "django_fusion.routes.models.crud",
        "django_fusion.routes.pages.views",
        "django_fusion.routes.pages.catalog",
        "django_fusion.routes.pages.handler",
        "django_fusion.routes.pages.paginators",
        "django_fusion.routes.http.detection",
        "django_fusion.routes.http.response",
        "django_fusion.routes.http.notifications",
        "django_fusion.routes.rendering.renderers",
        "django_fusion.routes.rendering.session",
        "django_fusion.routes.rendering.template_resolver",
    )

    for module_name in modules:
        assert import_module(module_name)


def test_old_route_implementation_files_are_removed():
    """The migration does not leave duplicate root implementation modules."""
    routes_dir = Path(__file__).parents[1] / "src" / "django_fusion" / "routes"
    old_names = (
        "base.py",
        "sites.py",
        "converters.py",
        "components.py",
        "fragments.py",
        "model.py",
        "other.py",
        "pages.py",
        "page_catalog.py",
        "page_handler.py",
        "paginators.py",
        "detection.py",
        "response.py",
        "notifications.py",
        "renderers.py",
        "session.py",
        "template_resolver.py",
        "dual_mode.py",
    )

    assert not any((routes_dir / name).exists() for name in old_names)


def test_canonical_route_symbols_bind_to_new_implementations():
    """Concrete route imports resolve to the moved implementation classes."""
    from django_fusion.routes.components.fragments import FragmentComponent
    from django_fusion.routes.components.fragments import (
        FragmentComponent as ConcreteFragment,
    )
    from django_fusion.routes.components.routable import RoutableComponent
    from django_fusion.routes.components.routable import (
        RoutableComponent as ConcreteRoutable,
    )
    from django_fusion.routes.core.base import BaseViewset, Viewset
    from django_fusion.routes.core.base import (
        BaseViewset as ConcreteBase,
        Viewset as ConcreteViewset,
    )
    from django_fusion.routes.core.sites import Application, Site
    from django_fusion.routes.core.sites import (
        Application as ConcreteApplication,
        Site as ConcreteSite,
    )
    from django_fusion.routes.rendering.session import FusionCodec
    from django_fusion.routes.rendering.session import FusionCodec as ConcreteCodec

    assert BaseViewset is ConcreteBase
    assert Viewset is ConcreteViewset
    assert Application is ConcreteApplication
    assert Site is ConcreteSite
    assert RoutableComponent is ConcreteRoutable
    assert FragmentComponent is ConcreteFragment
    assert FusionCodec is ConcreteCodec


def test_template_resolver_uses_canonical_package_template_name():
    """The resolver returns a direct name loadable from package templates."""
    from django.template.loader import get_template

    from django_fusion.routes.rendering.template_resolver import TemplateResolverMixin

    class ResolverView(TemplateResolverMixin):
        template_name = "components/form/form_field.html"

    template_name = ResolverView().get_template_names()[0]
    assert template_name == "components/form/form_field.html"
    template = get_template(template_name)
    assert template.template.name == template_name
