"""Unit tests for ``RoleBasedAccessMiddleware``.

Tests cover:

- View-level ``required_groups`` (any / all)
- View-level ``permission_required`` / ``required_permissions``
- URL-rule settings (``ROLE_BASED_ACCESS``)
- Superuser / staff bypass
- Public-path bypass
- Unauthenticated bypass
- ``require_groups`` / ``require_permissions`` decorators
- Helper functions (``_check_groups``, ``_check_permissions``, ``_match_url_pattern``)

Run with::

    cd libs/django-fusion && uv run pytest tests/test_role_based_access_middleware.py -v
"""

from __future__ import annotations

from typing import Any

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, override_settings

# Tests use the database (User.objects.create_user, etc.).  Tables are
# created by ``_django_settings.configure()`` at conftest time via
# ``migrate --run-syncdb``, so the ``django_db`` marker is not needed.
pytestmark = [pytest.mark.django_db(transaction=False)]

from django_fusion.core.middlewares.access import (
    RoleBasedAccessMiddleware,
    _check_groups,
    _check_permissions,
    _get_group_names,
    _get_view_attribute,
    _match_url_pattern,
    require_groups,
    require_permissions,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def get_response() -> Any:
    """A minimal ``get_response`` callable for middleware instantiation."""
    def _get_response(request: Any) -> HttpResponse:
        return HttpResponse("OK")
    return _get_response


@pytest.fixture
def middleware(get_response: Any) -> RoleBasedAccessMiddleware:
    return RoleBasedAccessMiddleware(get_response)


@pytest.fixture
def rf() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def admin_group() -> Group:
    group, _ = Group.objects.get_or_create(name="admin")
    return group


@pytest.fixture
def manager_group() -> Group:
    group, _ = Group.objects.get_or_create(name="manager")
    return group


@pytest.fixture
def editor_group() -> Group:
    group, _ = Group.objects.get_or_create(name="editor")
    return group


@pytest.fixture
def test_content_type() -> ContentType:
    ct, _ = ContentType.objects.get_or_create(app_label="test", model="dummy")
    return ct


@pytest.fixture
def view_permission(test_content_type: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="view_dummy",
        content_type=test_content_type,
        defaults={"name": "Can view dummy"},
    )
    return perm


@pytest.fixture
def change_permission(test_content_type: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="change_dummy",
        content_type=test_content_type,
        defaults={"name": "Can change dummy"},
    )
    return perm


@pytest.fixture
def admin_user(admin_group: Group) -> User:
    user = User.objects.create_user(
        username="admin_user",
        email="admin@example.com",
        password="secret",
    )
    user.groups.add(admin_group)
    return user


@pytest.fixture
def superuser_user() -> User:
    return User.objects.create_superuser(
        username="superuser",
        email="super@example.com",
        password="secret",
    )


@pytest.fixture
def staff_user() -> User:
    return User.objects.create_user(
        username="staff_user",
        email="staff@example.com",
        password="secret",
        is_staff=True,
    )


@pytest.fixture
def regular_user() -> User:
    return User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="secret",
    )


# ==============================================================================
# Helper tests
# ==============================================================================


class TestGetGroupNames:
    def test_authenticated_user(self, admin_user: User, admin_group: Group) -> None:
        names = _get_group_names(admin_user)
        assert "admin" in names

    def test_anonymous_user(self) -> None:
        names = _get_group_names(AnonymousUser())
        assert names == set()


class TestCheckGroups:
    def test_any_group_success(self) -> None:
        assert _check_groups({"admin", "user"}, ["admin"], require_all=False) is True

    def test_any_group_failure(self) -> None:
        assert _check_groups({"user"}, ["admin"], require_all=False) is False

    def test_all_groups_success(self) -> None:
        assert _check_groups({"admin", "editor"}, ["admin", "editor"], require_all=True) is True

    def test_all_groups_failure(self) -> None:
        assert _check_groups({"admin"}, ["admin", "editor"], require_all=True) is False

    def test_empty_required(self) -> None:
        assert _check_groups({"admin"}, [], require_all=False) is True
        assert _check_groups({"admin"}, [], require_all=True) is True


class TestCheckPermissions:
    def test_single_permission_success(self, view_permission: Permission, admin_user: User) -> None:
        admin_user.user_permissions.add(view_permission)
        assert _check_permissions(admin_user, ["test.view_dummy"]) is True

    def test_single_permission_failure(self, admin_user: User) -> None:
        assert _check_permissions(admin_user, ["test.view_dummy"]) is False

    def test_all_permissions_success(
        self, view_permission: Permission, change_permission: Permission, admin_user: User
    ) -> None:
        admin_user.user_permissions.add(view_permission, change_permission)
        assert _check_permissions(admin_user, ["test.view_dummy", "test.change_dummy"]) is True

    def test_missing_one_permission(
        self, view_permission: Permission, admin_user: User
    ) -> None:
        admin_user.user_permissions.add(view_permission)
        assert _check_permissions(admin_user, ["test.view_dummy", "test.change_dummy"]) is False

    def test_empty_required(self, admin_user: User) -> None:
        assert _check_permissions(admin_user, []) is True


class TestGetViewAttribute:
    def test_class_based_view(self) -> None:
        class MyView:
            required_groups = ["admin"]
            view_class = True  # placeholder for the real CBV marker

        # Simulate a class-based view's ``as_view()`` wrapper
        def view_func(request: Any) -> HttpResponse:
            return HttpResponse()

        view_func.view_class = MyView
        assert _get_view_attribute(view_func, "required_groups") == ["admin"]
        assert _get_view_attribute(view_func, "nonexistent", "fallback") == "fallback"

    def test_function_based_view(self) -> None:
        def view_func(request: Any) -> HttpResponse:
            return HttpResponse()

        view_func.required_groups = ["admin"]  # type: ignore[attr-defined]
        assert _get_view_attribute(view_func, "required_groups") == ["admin"]

    def test_decorated_view(self) -> None:
        def inner(request: Any) -> HttpResponse:
            return HttpResponse()

        def decorator(f: Any) -> Any:
            def wrapper(request: Any) -> HttpResponse:
                return f(request)
            wrapper.__wrapped__ = f
            return wrapper

        inner.required_groups = ["admin"]  # type: ignore[attr-defined]
        wrapped = decorator(inner)
        assert _get_view_attribute(wrapped, "required_groups") == ["admin"]


class TestMatchUrlPattern:
    def test_exact_match(self) -> None:
        rules = {"/admin/": {"groups": ["admin"]}}
        assert _match_url_pattern("/admin/", rules) == {"groups": ["admin"]}

    def test_prefix_match(self) -> None:
        rules = {"/admin/": {"groups": ["admin"]}}
        assert _match_url_pattern("/admin/users/", rules) == {"groups": ["admin"]}

    def test_no_match(self) -> None:
        rules = {"/admin/": {"groups": ["admin"]}}
        assert _match_url_pattern("/public/", rules) is None

    def test_empty_rules(self) -> None:
        assert _match_url_pattern("/admin/", {}) is None


# ==============================================================================
# Decorator tests
# ==============================================================================


class TestRequireGroupsDecorator:
    def test_any_group(self) -> None:
        @require_groups("admin", "manager")
        def my_view(request: Any) -> HttpResponse:
            return HttpResponse()

        assert my_view.required_groups == ["admin", "manager"]  # type: ignore[attr-defined]

    def test_all_groups(self) -> None:
        @require_groups("admin", "editor", all_groups=True)
        def my_view(request: Any) -> HttpResponse:
            return HttpResponse()

        assert my_view.required_groups_all == ["admin", "editor"]  # type: ignore[attr-defined]


class TestRequirePermissionsDecorator:
    def test_sets_required_permissions(self) -> None:
        @require_permissions("app.view_dummy", "app.change_dummy")
        def my_view(request: Any) -> HttpResponse:
            return HttpResponse()

        assert my_view.required_permissions == ["app.view_dummy", "app.change_dummy"]  # type: ignore[attr-defined]


# ==============================================================================
# Middleware: process_view tests
# ==============================================================================


class TestProcessViewBypass:
    """Tests for bypass conditions (superuser, staff, unauthenticated)."""

    def test_superuser_bypass(
        self, middleware: RoleBasedAccessMiddleware, rf: RequestFactory, superuser_user: User
    ) -> None:
        request = rf.get("/admin/")
        request.user = superuser_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None  # superuser always passes

    def test_staff_bypass_default(
        self, middleware: RoleBasedAccessMiddleware, rf: RequestFactory, staff_user: User
    ) -> None:
        request = rf.get("/admin/")
        request.user = staff_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None  # staff bypass by default

    @override_settings(ROLE_BASED_ACCESS_STAFF_BYPASS=False)
    def test_staff_bypass_disabled_grants_denied(
        self, middleware: RoleBasedAccessMiddleware, rf: RequestFactory, staff_user: User
    ) -> None:
        """With staff bypass disabled, staff without required groups get 403."""
        request = rf.get("/admin/")
        request.user = staff_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_groups = ["admin"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is not None
        assert result.status_code == 403

    @override_settings(ROLE_BASED_ACCESS_STAFF_BYPASS=True)
    def test_staff_bypass_enabled_allows_staff(
        self, middleware: RoleBasedAccessMiddleware, rf: RequestFactory, staff_user: User
    ) -> None:
        """With staff bypass enabled, staff pass even without required groups."""
        request = rf.get("/admin/")
        request.user = staff_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_groups = ["admin"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None  # staff bypass returns None (allow)

    def test_unauthenticated_bypass(
        self, middleware: RoleBasedAccessMiddleware, rf: RequestFactory
    ) -> None:
        request = rf.get("/admin/")
        request.user = AnonymousUser()

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None  # anonymous passes through (auth middleware handles login)

    @override_settings(ROLE_BASED_ACCESS_PUBLIC_PATHS=["/public/", "/login/"])
    def test_public_path_bypass(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
    ) -> None:
        request = rf.get("/public/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None  # public path bypasses checks


class TestProcessViewRequiredGroups:
    """Tests for view-level ``required_groups`` attribute."""

    def test_has_group_success(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
    ) -> None:
        request = rf.get("/dashboard/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_groups = ["admin"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None

    def test_has_group_failure(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        regular_user: User,
    ) -> None:
        request = rf.get("/dashboard/")
        request.user = regular_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_groups = ["admin"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is not None
        assert result.status_code == 403

    def test_any_group_success(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
        manager_group: Group,
    ) -> None:
        request = rf.get("/dashboard/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_groups = ["admin", "manager"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None

    def test_all_groups_failure(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
    ) -> None:
        request = rf.get("/dashboard/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_groups_all = ["admin", "editor"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is not None
        assert result.status_code == 403


class TestProcessViewRequiredPermissions:
    """Tests for view-level ``permission_required`` and ``required_permissions``."""

    def test_permission_required_string_success(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
        view_permission: Permission,
    ) -> None:
        admin_user.user_permissions.add(view_permission)
        request = rf.get("/reports/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.permission_required = "test.view_dummy"  # type: ignore[assignment]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None

    def test_permission_required_string_failure(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
    ) -> None:
        request = rf.get("/reports/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.permission_required = "test.view_dummy"  # type: ignore[assignment]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is not None
        assert result.status_code == 403

    def test_required_permissions_success(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
        view_permission: Permission,
        change_permission: Permission,
    ) -> None:
        admin_user.user_permissions.add(view_permission, change_permission)
        request = rf.get("/reports/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_permissions = ["test.view_dummy", "test.change_dummy"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None

    def test_required_permissions_failure(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
        view_permission: Permission,
    ) -> None:
        admin_user.user_permissions.add(view_permission)
        request = rf.get("/reports/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        dummy_view.required_permissions = ["test.view_dummy", "test.change_dummy"]  # type: ignore[attr-defined]

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is not None
        assert result.status_code == 403


class TestProcessViewUrlRules:
    """Tests for ``settings.ROLE_BASED_ACCESS`` URL-pattern rules."""

    @override_settings(ROLE_BASED_ACCESS={"/admin/": {"groups": ["admin"]}})
    def test_url_rule_groups_success(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
    ) -> None:
        request = rf.get("/admin/dashboard/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None

    @override_settings(ROLE_BASED_ACCESS={"/admin/": {"groups": ["admin"]}})
    def test_url_rule_groups_failure(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        regular_user: User,
    ) -> None:
        request = rf.get("/admin/dashboard/")
        request.user = regular_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is not None
        assert result.status_code == 403

    @override_settings(ROLE_BASED_ACCESS={
        "/reports/": {"permissions": ["test.view_dummy"]}
    })
    def test_url_rule_permissions_success(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        admin_user: User,
        view_permission: Permission,
    ) -> None:
        admin_user.user_permissions.add(view_permission)
        request = rf.get("/reports/")
        request.user = admin_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None

    @override_settings(ROLE_BASED_ACCESS={"/public/": None})
    def test_no_rules_configured(
        self,
        middleware: RoleBasedAccessMiddleware,
        rf: RequestFactory,
        regular_user: User,
    ) -> None:
        request = rf.get("/any/")
        request.user = regular_user

        def dummy_view(request: Any) -> HttpResponse:
            return HttpResponse()

        result = middleware.process_view(request, dummy_view, [], {})
        assert result is None  # No matching rule → pass


# ==============================================================================
# Import smoke test
# ==============================================================================


def test_middleware_importable() -> None:
    """RoleBasedAccessMiddleware is importable from the canonical path."""
    from django_fusion.core.middlewares.access import (
        RoleBasedAccessMiddleware as Imported,
    )
    from django_fusion.core.middlewares import (
        RoleBasedAccessMiddleware as FromPackage,
    )

    assert Imported is FromPackage


# ==============================================================================
# HTMX-aware error response
# ==============================================================================


def test_htmx_denied_response(middleware: RoleBasedAccessMiddleware, rf: RequestFactory) -> None:
    """HTMX requests get a 403 with the 403 template rendered."""
    request = rf.get("/admin/", HTTP_HX_REQUEST="true")
    request.user = AnonymousUser()
    # Simulate an authenticated user who lacks groups
    regular = User.objects.create_user(username="test", password="x")
    request.user = regular

    def dummy_view(request: Any) -> HttpResponse:
        return HttpResponse()

    dummy_view.required_groups = ["admin"]  # type: ignore[attr-defined]

    result = middleware.process_view(request, dummy_view, [], {})
    assert result is not None
    assert result.status_code == 403


def test_denied_response_non_htmx(
    middleware: RoleBasedAccessMiddleware, rf: RequestFactory
) -> None:
    """Non-HTMX requests get a 403 with the 403 template rendered."""
    request = rf.get("/admin/")
    regular = User.objects.create_user(username="test2", password="x")
    request.user = regular

    def dummy_view(request: Any) -> HttpResponse:
        return HttpResponse()

    dummy_view.required_groups = ["admin"]  # type: ignore[attr-defined]

    result = middleware.process_view(request, dummy_view, [], {})
    assert result is not None
    assert result.status_code == 403
