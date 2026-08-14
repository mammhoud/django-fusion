"""
LMS Fusion — Routable Components Module Configuration
======================================================

Defines the Application and Module hierarchy for the routable-components
routing system. Coexists with the existing manual URL routing in apps/urls.py.

Wire into projects/urls.py::

    from apps.core.routes import module
    urlpatterns += [path("osoul/", include((module.urls[0], module.urls[1]), namespace=module.urls[2]))]

Generated URL prefix: /osoul/
  /osoul/lms/dashboard/
  /osoul/lms/courses/list-fragment/   (HTMX only)
  /osoul/blog/posts/list-fragment/    (HTMX only)
  /osoul/blog/posts/create-fragment/  (HTMX only)
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.core.sites import Application
from django_fusion.routes.core.sites import Module
from django_fusion.routes.core.base import viewprop

# ---------------------------------------------------------------------------
# LMS Application
# ---------------------------------------------------------------------------

class LMSApp(Application):
    """Learning Management System — staff only.

    Inherits ``NotificationMixin`` from ``Application`` (merged from
    ``PageHandler``), so child ``RoutableComponent`` views (dashboard,
    enrollment, course management) automatically get ``add_success()``,
    ``add_error()``, and SSE streaming for enrollment toasts and alerts.
    """

    title = "Learning"
    icon = "school"
    app_name = "lms"

    @viewprop
    def viewsets(self):
        # Lazy import to avoid circular dependencies during module load
        from apps.learning.components import (
            CourseListFragment,
            DashboardComponent,
            PrivacyPageFragment,
            StaticPageFragment,
        )
        from apps.learning.viewsets import CourseViewset, EnrollmentViewset
        return [
            DashboardComponent(),
            CourseViewset(),
            EnrollmentViewset(),
            CourseListFragment(),
            PrivacyPageFragment(),
            StaticPageFragment("home"),
            StaticPageFragment("about"),
            StaticPageFragment("team"),
            StaticPageFragment("services"),
            StaticPageFragment("faq"),
            StaticPageFragment("contact"),
        ]

    def application_context(self, request: Any) -> dict[str, Any]:
        """Inject LMS-level context: branding, staff status, auth."""
        user = getattr(request, "user", None)
        return {
            "lms_title": self.title,
            "lms_icon": self.icon,
            "is_staff": user.is_staff if user and user.is_authenticated else False,
        }

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated and user.is_staff


# ---------------------------------------------------------------------------
# Blog Application
# ---------------------------------------------------------------------------

class BlogApp(Application):
    """Blog — public read, staff write.

    Inherits ``NotificationMixin`` from ``Application`` (merged from
    ``PageHandler``), so child ``RoutableComponent`` views (post editor,
    category manager) automatically get ``add_success()`` and
    ``add_error()`` for publish/save toasts.
    """

    title = "Blog"
    icon = "article"
    app_name = "blog"

    @viewprop
    def viewsets(self):
        from apps.pages.blog.components import BlogPostCreateFragment, BlogPostListFragment
        from apps.pages.blog.viewsets import BlogCategoryViewset, BlogPostViewset
        return [
            BlogPostViewset(),
            BlogCategoryViewset(),
            BlogPostListFragment(),
            BlogPostCreateFragment(),
        ]

    def application_context(self, request: Any) -> dict[str, Any]:
        """Inject blog-level context for all blog components."""
        user = getattr(request, "user", None)
        return {
            "blog_title": self.title,
            "blog_icon": self.icon,
            "can_write": (
                user.is_authenticated and user.is_staff
                if user else False
            ),
        }

    def has_view_permission(self, user, obj=None):
        return True  # Public


# ---------------------------------------------------------------------------
# Module — lazy creation to avoid circular imports during module load.
# ---------------------------------------------------------------------------

_module: Module | None = None


def get_module() -> Module:
    """Build the Module once, memoized.

    Lazily creates the Module instance after Django has fully initialized
    the app registry.  Applications are imported at the top of this
    module, so their ``viewsets`` lazy-import components only when first
    accessed.
    """
    global _module
    if _module is None:
        _module = Module(
            title="LMS Fusion",
            viewsets=[
                LMSApp(),
                BlogApp(),
            ],
        )
    return _module


# Expose as 'module'.
module = get_module()
