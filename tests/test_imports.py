"""Smoke tests for canonical public import paths."""

import sys

import pytest
from django.test import RequestFactory


def test_middleware_imports():
    """ErrorTrackerMiddleware is importable from core middlewares."""
    from django_fusion.core.middlewares import (
        ErrorTrackerMiddleware as Middleware,
    )
    from django_fusion.core.middlewares.errors import (
        ErrorTrackerMiddleware,
    )

    assert ErrorTrackerMiddleware is Middleware


def test_service_public_imports_use_canonical_modules():
    """Service exports resolve to the directly maintained implementations."""
    from django_fusion.services import BaseService, TokenService, dispatch_job
    from django_fusion.services.base import BaseService as CanonicalBaseService
    from django_fusion.services.jobs import dispatch_job as canonical_dispatch_job
    from django_fusion.services.token import TokenService as CanonicalTokenService

    assert BaseService is CanonicalBaseService
    assert TokenService is CanonicalTokenService
    assert dispatch_job is canonical_dispatch_job


def test_shared_model_bases_are_public_and_abstract():
    """Promoted domain behavior is available from the package API."""
    from django_fusion.models import (
        AbstractBrandSettings,
        AbstractCertificationTemplate,
        AbstractCoupon,
        AbstractCouponUsage,
        AbstractEmailSettings,
        AbstractGlobalSettings,
        AbstractLocalizedSettings,
        AbstractNewsletter,
        AbstractNewsletterSubscription,
        AbstractWorkspace,
    )

    for model in (
        AbstractWorkspace,
        AbstractCoupon,
        AbstractCouponUsage,
        AbstractCertificationTemplate,
        AbstractNewsletter,
        AbstractLocalizedSettings,
        AbstractBrandSettings,
        AbstractEmailSettings,
        AbstractGlobalSettings,
        AbstractNewsletterSubscription,
    ):
        assert model._meta.abstract is True


def test_context_exports_canonical_fragment_handler_without_dead_detection():
    """The context module exposes one handler implementation and no dead predicate."""
    from django_fusion.core.context import _context_mixins
    from django_fusion.core.context.context import FragmentHandlerMixin
    from django_fusion.core.context.context import (
        FragmentHandlerMixin as ContextFragmentHandlerMixin,
    )

    assert ContextFragmentHandlerMixin is FragmentHandlerMixin
    assert not hasattr(_context_mixins, "is_fragment_request")


def test_role_manager_defaults_are_preserved_from_canonical_module():
    from django_fusion.management.managers.role_hierarchy import RoleHierarchyManager

    manager = RoleHierarchyManager()
    assert manager.get_role_hierarchy("admin") == ["admin", "supervisor", "user"]
    assert "auth.view_user" in manager.get_all_permissions_for_role("admin")


def test_supports_htmx_warns_and_preserves_behavior():
    """The deprecated wrapper still delegates to the canonical HTMX predicate."""
    from django_fusion.plugins.htmx import supports_htmx

    request = RequestFactory().get("/", HTTP_HX_REQUEST="true")
    with pytest.warns(DeprecationWarning, match="use is_htmx_request"):
        assert supports_htmx(request) is True


def test_dispatch_job_reports_missing_optional_queue_dependency(monkeypatch):
    """Job dispatch fails clearly when neither logging nor django-rq is available."""
    from django_fusion.services import jobs

    monkeypatch.setattr(jobs, "_get_task_log_model", lambda: None)
    monkeypatch.setitem(sys.modules, "django_rq", None)

    with pytest.raises(RuntimeError, match="requires django-rq"):
        jobs.dispatch_job(lambda: None)


def test_route_tree_contract_is_covered():
    """The physical route-tree migration has a dedicated regression suite."""
    from django_fusion.routes.components.routable import RoutableComponent
    from django_fusion.routes.components.routable import (
        RoutableComponent as ConcreteRoutable,
    )

    assert RoutableComponent is ConcreteRoutable


def test_token_service_supports_model_free_action_validation():
    """The class-level action API works without a model-backed service."""
    from django_fusion.services import TokenService

    validation = TokenService.validate_action_token(
        "not-a-token", expected_action="update"
    )
    assert isinstance(validation, dict)
    assert "valid" in validation
