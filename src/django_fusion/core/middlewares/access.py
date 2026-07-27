"""
RoleBasedAccessMiddleware
=========================
Enforces group- and permission-based access control at the middleware layer,
before requests reach views.  Designed for Django's built-in ``Group`` and
``Permission`` models, following the django-fusion middleware conventions.

Configuration (*via Django settings*)::

    ROLE_BASED_ACCESS = {
        # URL prefix → rules (user must match at least one rule group)
        "/admin/": {"groups": ["admin"]},
        "/dashboard/": {"groups": ["admin", "manager"]},
        "/reports/": {"permissions": ["reports.view_report"]},
    }

    ROLE_BASED_ACCESS_DENIED_VIEW = "admin:login"   # optional redirect target

View-level decoration (preferred over URL-pattern rules)::

    # Class-based view: set class attributes
    class MyView(View):
        required_groups = ["admin", "manager"]      # user needs ANY listed group
        required_groups_all = ["admin", "editor"]    # user needs ALL listed groups
        permission_required = "app.view_model"      # Django standard pattern

    # Function-based view: set function attributes
    @staff_member_required
    def my_view(request):
        ...

    my_view.permission_required = "app.view_model"

The middleware checks (in order):

1. ``required_groups`` — user must belong to **any** of the listed groups.
2. ``required_groups_all`` — user must belong to **every** listed group.
3. ``permission_required`` (Django standard) — user must have the permission.
4. ``required_permissions`` — user must have **every** listed permission.
5. ``ROLE_BASED_ACCESS`` setting — URL-prefix-based fallback rules.

Usage (add to ``MIDDLEWARE`` after ``AuthenticationMiddleware``)::

    MIDDLEWARE = [
        ...
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django_fusion.core.middlewares.access.RoleBasedAccessMiddleware",
        ...
    ]

HTMX-friendly — returns a ``PermissionDenied`` response that HTMX can
display as a fragment (status 403 + ``X-Up-Target`` awareness).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.urls import ResolverMatch

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers — extracted for testability
# ---------------------------------------------------------------------------

def _get_view_attribute(view_func: Callable, attr: str, default: Any = None) -> Any:
    """Read an attribute from a view callable.

    Handles both function views (via ``__dict__`` or ``__wrapped__``) and
    class-based views (via ``view_class``).  Traverses multiple levels of
    ``__wrapped__`` to support stacked decorators.
    """
    # Class-based view (``as_view()`` sets ``view_class`` on the wrapper)
    view_class = getattr(view_func, "view_class", None)
    if view_class is not None:
        return getattr(view_class, attr, default)

    # Traverse ``__wrapped__`` chain (supports stacked decorators)
    target = view_func
    visited = {view_func}
    while True:
        result = getattr(target, attr, None)
        if result is not None:
            return result
        wrapped = getattr(target, "__wrapped__", None)
        if wrapped is None or wrapped in visited:
            break
        visited.add(wrapped)
        target = wrapped

    return default


def _get_group_names(user: Any) -> set[str]:
    """Return the set of Django group names for *user*.

    Works with both authenticated users and ``AnonymousUser`` (returns empty set).
    """
    if user.is_authenticated and hasattr(user, "groups"):
        return set(user.groups.values_list("name", flat=True))
    return set()


def _check_groups(user_groups: set[str], required: list[str], require_all: bool = False) -> bool:
    """Check whether *user_groups* satisfy *required* groups.

    *require_all=False* (default) → user needs **any** of the listed groups.
    *require_all=True*            → user needs **every** listed group.
    """
    if not required:
        return True
    required_set = set(required)
    if require_all:
        return required_set.issubset(user_groups)
    return bool(user_groups & required_set)


def _check_permissions(user: Any, required: list[str]) -> bool:
    """Check whether *user* has **every** permission in *required*."""
    if not required:
        return True
    return all(user.has_perm(p) for p in required)


def _match_url_pattern(path: str, rules: dict[str, dict]) -> dict | None:
    """Find the first matching URL rule from the ``ROLE_BASED_ACCESS`` dict.

    Rules are prefix-matched by default.  Exact match is tried first for a
    fast path; then the longest-matching prefix wins.

    If advanced regex matching is needed in the future, use a separate
    setting (e.g. ``ROLE_BASED_ACCESS_REGEX``) instead of embedding patterns
    in the prefix key, since Python's ``r"..."`` literal syntax does not
    survive JSON/YAML deserialization.
    """
    # Exact match first (fast path)
    if path in rules:
        return rules[path]

    # Prefix match — longest matching prefix wins
    candidates = [(prefix, rule) for prefix, rule in rules.items() if path.startswith(prefix)]
    if not candidates:
        return None
    # Sort by prefix length descending so the most specific match is used
    candidates.sort(key=lambda item: len(item[0]), reverse=True)
    return candidates[0][1]


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


class RoleBasedAccessMiddleware:
    """Enforce group- and permission-based access at the middleware level.

    Checks are performed in ``process_view()`` after the resolver match is
    available but before the view is called.  This gives access to the view
    function/class attributes and the matched URL name.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        return self.get_response(request)

    @staticmethod
    def _denied_response(request: HttpRequest, reason: str = "") -> HttpResponse:
        """Return a 403 response, HTMX-aware when possible."""
        from django.template.exceptions import TemplateDoesNotExist

        template_name = "plugins/errors/403.html"
        context = {"reason": reason, "is_htmx": getattr(request, "is_htmx", False)}

        # HTMX — attempt fragment render, fall back to plain 403
        if getattr(request, "is_htmx", False):
            try:
                return render(request, template_name, context, status=403)
            except TemplateDoesNotExist:
                return HttpResponse(
                    f"<h1>403 Forbidden</h1><p>{reason}</p>",
                    status=403,
                    content_type="text/html",
                )

        # Redirect to a named denied-view if configured
        denied_view = getattr(settings, "ROLE_BASED_ACCESS_DENIED_VIEW", None)
        if denied_view and request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.urls import reverse
            try:
                return redirect(reverse(denied_view))
            except Exception:
                pass

        # Template render with fallback
        try:
            return render(request, template_name, context, status=403)
        except TemplateDoesNotExist:
            return HttpResponse(
                f"<h1>403 Forbidden</h1><p>{reason}</p>",
                status=403,
                content_type="text/html",
            )

    # ------------------------------------------------------------------
    # Core check methods — override in subclasses for custom logic
    # ------------------------------------------------------------------

    def check_view_attributes(self, request: HttpRequest, view_func: Callable) -> str | None:
        """Check view-level ``required_groups`` / ``permission_required``.

        Returns ``None`` on success, or an error message string on failure.
        """
        required_groups = _get_view_attribute(view_func, "required_groups", None)
        required_groups_all = _get_view_attribute(view_func, "required_groups_all", None)
        permission_required = _get_view_attribute(view_func, "permission_required", None)
        required_permissions = _get_view_attribute(view_func, "required_permissions", None)

        user = request.user
        user_groups = _get_group_names(user)

        # 1. ``required_groups`` — user needs ANY listed group
        if required_groups is not None:
            if not _check_groups(user_groups, required_groups, require_all=False):
                return (
                    f"User '{user}' does not belong to any required group. "
                    f"Required (any): {required_groups}"
                )

        # 2. ``required_groups_all`` — user needs ALL listed groups
        if required_groups_all is not None:
            if not _check_groups(user_groups, required_groups_all, require_all=True):
                return (
                    f"User '{user}' is missing one or more required groups. "
                    f"Required (all): {required_groups_all}"
                )

        # 3. ``permission_required`` (Django standard, string or list)
        if permission_required is not None:
            perms = permission_required if isinstance(permission_required, list) else [permission_required]
            if not _check_permissions(user, perms):
                return (
                    f"User '{user}' lacks required permission(s): {permission_required}"
                )

        # 4. ``required_permissions`` — user needs ALL listed permissions
        if required_permissions is not None:
            if not _check_permissions(user, required_permissions):
                return (
                    f"User '{user}' lacks required permission(s): {required_permissions}"
                )

        return None

    def check_url_rules(self, request: HttpRequest) -> str | None:
        """Check URL-pattern rules from ``settings.ROLE_BASED_ACCESS``.

        Returns ``None`` on success, or an error message string on failure.
        """
        url_rules = getattr(settings, "ROLE_BASED_ACCESS", None)
        if not url_rules:
            return None

        path = request.path_info
        rule = _match_url_pattern(path, url_rules)
        if rule is None:
            return None

        user = request.user
        user_groups = _get_group_names(user)

        groups = rule.get("groups")
        permissions = rule.get("permissions")
        require_all = rule.get("require_all", False)

        if groups:
            if not _check_groups(user_groups, groups, require_all=require_all):
                return (
                    f"User '{user}' does not satisfy URL-rule group requirements "
                    f"for '{path}'. Required: {groups}"
                )

        if permissions:
            if not _check_permissions(user, permissions):
                return (
                    f"User '{user}' lacks URL-rule permission(s) for '{path}': {permissions}"
                )

        return None

    def is_public_path(self, request: HttpRequest) -> bool:
        """Return ``True`` if *request.path* is in the public bypass list.

        Override in subclasses to add custom public-path logic.
        """
        public_paths = getattr(settings, "ROLE_BASED_ACCESS_PUBLIC_PATHS", None)
        if public_paths is None:
            return False
        path = request.path_info
        return any(path.startswith(p) for p in public_paths)

    # ------------------------------------------------------------------
    # Django middleware hook
    # ------------------------------------------------------------------

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: list,
        view_kwargs: dict,
    ) -> HttpResponse | None:
        """Intercept requests and enforce group/permission checks.

        Checks (in order):

        1. Superuser / staff bypass — ``is_superuser`` or ``is_staff`` skip all checks.
        2. Public-path bypass — paths listed in ``ROLE_BASED_ACCESS_PUBLIC_PATHS``.
        3. View-level attributes — ``required_groups``, ``permission_required``, etc.
        4. URL-rule settings — ``ROLE_BASED_ACCESS`` dict.

        Returns ``None`` (allow request) or a ``HttpResponse`` (deny, 403).
        """
        # --- Bypass: superuser / staff ---
        user = request.user
        if user.is_superuser:
            return None

        staff_bypass = getattr(settings, "ROLE_BASED_ACCESS_STAFF_BYPASS", True)
        if staff_bypass and user.is_staff:
            return None

        # --- Bypass: public paths ---
        if self.is_public_path(request):
            return None

        # --- Bypass: unauthenticated ---
        if isinstance(user, AnonymousUser):
            return None

        # --- Check 1: view-level attributes ---
        error = self.check_view_attributes(request, view_func)
        if error is not None:
            logger.warning("Access denied (view attributes): %s", error)
            return self._denied_response(request, reason=error)

        # --- Check 2: URL-pattern rules ---
        error = self.check_url_rules(request)
        if error is not None:
            logger.warning("Access denied (URL rules): %s", error)
            return self._denied_response(request, reason=error)

        return None


# ---------------------------------------------------------------------------
# Decorator helper — mark a view with required groups
# ---------------------------------------------------------------------------


def require_groups(*groups: str, all_groups: bool = False):
    """Decorator that sets ``required_groups`` on a view function.

    Usage::

        @require_groups("admin", "manager")
        def my_view(request):
            ...

        @require_groups("admin", "editor", all_groups=True)
        def restricted_view(request):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        if all_groups:
            view_func.required_groups_all = list(groups)  # type: ignore[attr-defined]
        else:
            view_func.required_groups = list(groups)  # type: ignore[attr-defined]
        return view_func
    return decorator


def require_permissions(*perms: str):
    """Decorator that sets ``required_permissions`` on a view function.

    Usage::

        @require_permissions("app.view_model", "app.change_model")
        def my_view(request):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        view_func.required_permissions = list(perms)  # type: ignore[attr-defined]
        return view_func
    return decorator


__all__ = [
    "RoleBasedAccessMiddleware",
    "require_groups",
    "require_permissions",
]
