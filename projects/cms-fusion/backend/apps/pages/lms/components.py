"""
LMS Fragment Components for fusion-cms.com
=============================================

HTMX fragment components for the Learning Management System.
These provide partial HTML responses for dynamic page updates.

Usage::

    from apps.pages.lms.components import CourseListFragment
    # Register in apps/pages/lms/application.py → LMSApp.viewsets
"""

from __future__ import annotations

import logging

from django.db.models import Q
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.components.dual_mode import FusionDualModeMixin
from django_fusion.routes.components.routable import RoutableComponent

logger = logging.getLogger(__name__)


class DashboardComponent(FusionDualModeMixin, RoutableComponent):
    """
    LMS Dashboard — full-page routable component with dual-mode rendering.

    URL: /app/lms/dashboard/

    * ``fusion_render_first=True``  → renders ``lms/dashboard.html`` (HTML).
    * ``fusion_render_first=False`` → returns codec-encoded JSON with the
      dashboard stats + Site navigation encapsulation.
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

    def get_fragment_data(self) -> dict:
        """Serialise dashboard data for data mode (fusion_render_first=False)."""
        return {
            "stats": self._get_stats(),
            "recent_enrollments": list(
                self._get_recent_enrollments().values(
                    "id", "enrolled_at", "student__username", "course__title"
                )
            ),
        }

    def _get_stats(self):
        from apps.pages.lms.models.courses import Course
        from apps.pages.lms.models.enrollment import Enrollment
        return {
            "total_courses": Course.objects.count(),
            "total_enrollments": Enrollment.objects.count(),
            "published_courses": Course.objects.filter(published=True).count(),
        }

    def _get_recent_enrollments(self):
        from apps.pages.lms.models.enrollment import Enrollment
        return Enrollment.objects.select_related("student", "course").order_by("-enrolled_at")[:10]


class StaticPageFragment(FragmentComponent):
    """
    Generic fragment for any ``STATIC_PAGES`` entry.

    Accept a ``slug`` parameter at construction time so a single class can
    serve ``home``, ``about``, ``team``, ``services``, ``faq``, ``contact``, etc.

    Fragment URL: /fragments/pages.<slug>/
    Template: pages/page.html (generic, renders all STATIC_PAGES block types)

    Usage (in routes.py)::

        StaticPageFragment("home"),
        StaticPageFragment("about"),
        StaticPageFragment("services"),
    """

    htmx_only = False
    show_in_menu = False
    template_name = "pages/page.html"

    def __init__(self, slug: str, **kwargs):
        self._slug = slug
        # Unique route per page to avoid route-name clashes
        sanitized = slug.replace("-", "_").replace("/", "_")
        self.route_name = f"static-{sanitized}-fragment"
        self.route_path = f"pages/{slug}/"
        self.fragment_name = f"pages.{sanitized}"
        super().__init__(**kwargs)

    def has_permission(self, user):
        return True

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        # Page data now comes from Wagtail API, not STATIC_PAGES
        context["page"] = {"slug": self._slug, "title": self._slug.replace("-", " ").title()}
        return context


class PrivacyPageFragment(StaticPageFragment):
    """
    Privacy policy rendered as a server-side fragment.

    Uses the ``pages/privacy.html`` template (custom privacy layout).
    All other static pages use the generic ``pages/page.html`` template.
    """

    template_name = "pages/privacy.html"

    def __init__(self, **kwargs):
        super().__init__("privacy", **kwargs)


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
        from apps.pages.lms.models.courses import Course
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
        from apps.pages.lms.models.courses import Course
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        return context


# ─── Course grid (HTMX action fragment) ────────────────────────────


class CourseGridFragment(FusionDualModeMixin, FragmentComponent):
    """GET /lms/courses/grid/ — Filtered course grid with pagination.

    Query params:
      q          — search query
      difficulty — difficulty level filter
      featured   — "true" to filter featured only
      page       — page number (default 1)

    Registered in ``LMSApp.viewsets`` (app_name="lms"), so the ``route_path``
    is relative to the ``lms/`` app prefix.
    """

    route_name = "course-grid"
    route_path = "courses/grid/"
    fragment_name = "htmx.course_grid"
    htmx_only = True

    def get_queryset(self):
        from django.db import models
        from apps.pages.lms.models import Course

        qs = Course.objects.filter(is_published=True, is_active=True).order_by(
            "-is_featured", "-created_at"
        )

        q = self.request.GET.get("q", "")
        if q:
            qs = qs.filter(
                models.Q(title__icontains=q)
                | models.Q(short_description__icontains=q)
            )

        difficulty = self.request.GET.get("difficulty", "")
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)

        featured = self.request.GET.get("featured", "")
        if featured == "true":
            qs = qs.filter(is_featured=True)

        return qs

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context

    def get_fragment_data(self) -> dict:
        """Serialise the course grid for data mode (fusion_render_first=False)."""
        qs = self.get_queryset()
        page = max(1, int(self.request.GET.get("page", 1)))
        per_page = 12
        total = qs.count()
        courses = qs[(page - 1) * per_page : page * per_page]

        return {
            "courses": [
                {
                    "id": c.pk, "title": c.title, "slug": c.slug,
                    "short_description": getattr(c, "short_description", ""),
                    "image_url": c.image.file.url if getattr(c, "image", None) else None,
                    "instructor": c.instructor.get_full_name() if getattr(c, "instructor", None) else "",
                    "price": float(getattr(c, "current_price", 0)),
                    "original_price": float(getattr(c, "original_price", 0))
                    if getattr(c, "original_price", 0) else None,
                    "difficulty": getattr(c, "difficulty_level", ""),
                    "rating": float(getattr(c, "average_rating", 0)),
                    "is_featured": getattr(c, "is_featured", False),
                }
                for c in courses
            ],
            "pagination": {
                "page": page, "per_page": per_page, "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
            "q": self.request.GET.get("q", ""),
        }


class CourseFiltersFragment(FusionDualModeMixin, FragmentComponent):
    """GET /lms/courses/filters/ — Course filter sidebar controls."""

    route_name = "course-filters"
    route_path = "courses/filters/"
    fragment_name = "htmx.course_filters"
    htmx_only = True

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        filters = self.get_fragment_data()
        context["languages"] = filters["languages"]
        context["difficulties"] = filters["difficulties"]
        return context

    def get_fragment_data(self) -> dict:
        try:
            from apps.pages.lms.models import Course

            qs = Course.objects.filter(is_published=True, is_active=True)
            languages = list(qs.values_list("language", flat=True).distinct().order_by("language"))
            difficulties = list(qs.values_list("difficulty_level", flat=True).distinct())
            return {
                "languages": [l for l in languages if l],
                "difficulties": [d for d in difficulties if d],
            }
        except Exception:
            logger.exception("Error loading course filters")
            return {"languages": [], "difficulties": []}


# ─── Dashboard KPIs (HTMX action fragment) ─────────────────────────


class DashboardKPIsFragment(FusionDualModeMixin, FragmentComponent):
    """GET /lms/dashboard/kpis/ — KPI metric cards for the dashboard.

    Registered in ``LMSApp.viewsets`` (app_name="lms"), so the ``route_path``
    is relative to the ``lms/`` app prefix.
    """

    route_name = "dashboard-kpis"
    route_path = "dashboard/kpis/"
    fragment_name = "htmx.dashboard_kpis"
    htmx_only = True

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["kpis"] = self.get_fragment_data().get("kpis", [])
        return context

    def get_fragment_data(self) -> dict:
        kpis = []

        try:
            if not self.request.user.is_authenticated:
                return {"kpis": kpis}

            from apps.pages.lms.models import Course
            from apps.pages.blog.models.post import BlogPost

            kpis.append({
                "icon": "book-open",
                "label": "Published Courses",
                "value": Course.objects.filter(is_published=True, is_active=True).count(),
                "color": "primary",
            })
            kpis.append({
                "icon": "newspaper",
                "label": "Blog Posts",
                "value": BlogPost.objects.filter(status="published").count(),
                "color": "accent",
            })

            student_enrollments = 0
            try:
                from apps.pages.lms.models import Enrollment
                student_enrollments = Enrollment.objects.count()
            except Exception:
                pass

            kpis.append({
                "icon": "users",
                "label": "Total Enrollments",
                "value": student_enrollments,
                "color": "secondary",
            })
            kpis.append({
                "icon": "trending-up",
                "label": "Active Students",
                "value": max(0, student_enrollments),
                "color": "success",
            })
        except Exception:
            logger.exception("Error loading dashboard KPIs")

        return {"kpis": kpis}
