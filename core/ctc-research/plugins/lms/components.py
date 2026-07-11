"""
LMS Fragment Components for ctc-research.com
=============================================

HTMX fragment components for the Learning Management System.
These provide partial HTML responses for dynamic page updates.

Usage::

    from plugins.lms.components import CourseListFragment
    # Register in apps/core/routes.py → LMSApp.viewsets
"""

from __future__ import annotations

from django.db.models import Q
from django_fusion.comp.routes import FragmentComponent, RoutableComponent


class DashboardComponent(RoutableComponent):
    """
    LMS Dashboard — full-page routable component.

    URL: /app/lms/dashboard/
    """

    route_name = "dashboard"
    route_path = "dashboard/"
    title = "Dashboard"
    page_title = "Dashboard"
    icon = "dashboard"
    menu_order = 1
    template_name = "lms/dashboard.html"

    def has_permission(self, user):
        return user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "stats": self._get_stats(),
            "recent_enrollments": self._get_recent_enrollments(),
        })
        return context

    def _get_stats(self):
        from plugins.lms.models.courses import Course
        from plugins.lms.models.enrollment import Enrollment
        return {
            "total_courses": Course.objects.count(),
            "total_enrollments": Enrollment.objects.count(),
            "published_courses": Course.objects.filter(published=True).count(),
        }

    def _get_recent_enrollments(self):
        from plugins.lms.models.enrollment import Enrollment
        return Enrollment.objects.select_related("student", "course").order_by("-enrolled_at")[:10]


class CourseListFragment(FragmentComponent):
    """
    Course list as HTMX fragment with pagination and search.

    URL: /app/lms/courses/list-fragment/
    Only responds to HTMX requests (htmx_only=True).

    Template: lms/fragments/course_list.html

    HTMX usage::

        <div id="course-list" data-fragment>
          <button hx-get="{% url 'lms:course-list-fragment' %}"
                  hx-target="#course-list"
                  hx-swap="innerHTML">
            Refresh
          </button>
        </div>
    """

    route_name = "course-list-fragment"
    route_path = "courses/list-fragment/"
    fragment_name = "lms.fragments.course_list"
    htmx_only = True
    paginate_by = 20
    show_in_menu = False  # Fragment — not shown in navigation

    def has_permission(self, user):
        return user.is_authenticated

    def get_queryset(self):
        from plugins.lms.models.courses import Course
        qs = Course.objects.filter(published=True).select_related("instructor")

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )

        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)

        return qs.order_by("-created_at")

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        # Add filter options
        from plugins.lms.models.courses import Course
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        return context
