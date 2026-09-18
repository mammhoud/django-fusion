"""
LMS Application for precis-lms.com
=====================================

Defines the ``LMSApp`` Application (routable-components hierarchy node)
for the Learning Management System. Kept in the LMS app so core routing
only assembles the ``Module`` from app-level Application classes.

Usage (in core/routes.py)::

    from apps.learning.application import LMSApp

    module = Module(title="LMS Fusion", viewsets=[LMSApp(), BlogApp()])
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.core.base import viewprop
from django_fusion.routes.core.sites import Application


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
            CourseFiltersFragment,
            CourseGridFragment,
            CourseListFragment,
            DashboardComponent,
            DashboardKPIsFragment,
            PrivacyPageFragment,
            StaticPageFragment,
        )
        from apps.learning.viewsets import CourseViewset, EnrollmentViewset
        return [
            DashboardComponent(),
            CourseViewset(),
            EnrollmentViewset(),
            CourseListFragment(),
            CourseGridFragment(),
            CourseFiltersFragment(),
            DashboardKPIsFragment(),
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


__all__ = ["LMSApp"]
