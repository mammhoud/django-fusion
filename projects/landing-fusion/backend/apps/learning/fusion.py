"""
Learning + profile — django-fusion Application routing.

The learner surface (catalog, course detail, dashboard, profile) is
registered as one ``Application`` with ``menu_path`` entries (name / icon /
title metadata) reusing the existing dual-mode views in ``apps.learning.views``:

* plain browser load → full document
* HTMX request       → fragment swap (``_is_htmx`` in each view)

Mounted at ``/learning/`` with the ``learning`` namespace (the same namespace
``apps.learning.urls`` exposed, so ``reverse("learning:course")`` and every
``{% url 'learning:...' %}`` keeps resolving). ``application_context()``
injects the learner navigation (Catalog / Dashboard / Profile) plus the site
name, and ``menu_items()`` exposes the menu metadata for side-nav renderers.
"""
from __future__ import annotations

from typing import Any

from django.urls import path

from django_fusion.routes.core.base import menu_path
from django_fusion.routes.core.sites import Application

from apps.learning import views
from apps.learning.api import courses as courses_api


class LearningApplication(Application):
    """Learner + profile routes, declared once with menu metadata."""

    title = "Learning"
    icon = "school"
    app_name = "learning"

    urlpatterns = [
        menu_path("", views.catalog, name="catalog", icon="storefront", title="Course catalog"),
        menu_path("course/<slug:slug>/", views.course_detail, name="course", icon="menu_book", title="Course"),
        path("course/<slug:slug>/watch/", views.course_watch, name="course_watch"),
        path("course/<slug:slug>/lesson/<int:lesson_id>/", views.course_watch, name="course_watch_lesson"),
        path("course/<slug:slug>/continue/", views.course_continue, name="course_continue"),
        menu_path("dashboard/", views.dashboard, name="dashboard", icon="dashboard", title="My dashboard"),
        menu_path("profile/", views.profile_dashboard, name="profile", icon="person", title="Profile"),
        path("course/<slug:slug>/enroll/", views.enroll, name="enroll"),
        path("course/<slug:slug>/wishlist/", views.toggle_wishlist, name="wishlist"),
        path("lesson/<int:lesson_id>/complete/", views.complete_lesson, name="complete_lesson"),
        path("lesson/<int:lesson_id>/navigate/", views.lesson_navigate, name="lesson_navigate"),
        path("enrollment/list/", views.enrollment_list, name="enrollment_list"),
        path("enrollment/<int:enrollment_id>/status/", views.enrollment_status_update, name="enrollment_status_update"),
        path("enrollment/form/<int:course_id>/", views.course_enrollment_form, name="course_enrollment_form"),
        path("api/courses/search/", courses_api.course_search_api, name="course_search_api"),
        path("api/courses/<slug:slug>/", courses_api.course_detail_api, name="course_detail_api"),
    ]

    def application_context(self, request: Any) -> dict[str, Any]:
        """Shared learner context: the app identity + the learner navigation."""
        return {
            "site_name": "Structa Cloud",
            "app_title": self.title,
            "app_icon": self.icon,
            "learner_nav": self.get_learner_nav(request),
        }

    def get_learner_nav(self, request: Any = None) -> list[dict[str, Any]]:
        """Learner navigation — Catalog / Dashboard / Profile with active state.

        Used by the templates (via the ``learner_nav`` context or the
        ``learning/partials/learner_nav.html`` partial) and by ``menu_items()``.
        """
        current = getattr(request, "path", "") if request else ""
        return [
            {
                "label": "Catalog",
                "href": "/learning/",
                "icon": "storefront",
                "active": current == "/learning/",
            },
            {
                "label": "Dashboard",
                "href": "/learning/dashboard/",
                "icon": "dashboard",
                "active": current.startswith("/learning/dashboard"),
            },
            {
                "label": "Profile",
                "href": "/learning/profile/",
                "icon": "person",
                "active": current.startswith("/learning/profile"),
            },
        ]


# Singleton — mounted once from the root URL conf under /learning/.
learning_application = LearningApplication()
