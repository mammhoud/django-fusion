"""
CTC Research — Routable Components Site Configuration
======================================================

Defines the Application and Site hierarchy for the new routable-components
routing system. This coexists with the existing manual URL routing in
apps/urls.py — no existing URLs are changed.

Wire into core/urls.py::

    from www.apps.core.routes import site
    urlpatterns += [path("osoul/", include(site.urls))]

Generated URL prefix: /osoul/
  /osoul/lms/dashboard/
  /osoul/lms/courses/
  /osoul/lms/courses/<pk>/detail/
  /osoul/lms/courses/<pk>/change/
  /osoul/lms/courses/<pk>/delete/
  /osoul/lms/courses/list-fragment/   (HTMX only)
  /osoul/blog/posts/
  /osoul/blog/posts/<pk>/detail/
  /osoul/blog/posts/list-fragment/    (HTMX only)
  /osoul/blog/posts/create-fragment/  (HTMX only)
"""

from __future__ import annotations

from django_osoul.routes import Application, Site

# ---------------------------------------------------------------------------
# LMS Application
# ---------------------------------------------------------------------------

class LMSApp(Application):
    """Learning Management System — staff only."""

    title = "Learning"
    icon = "school"
    app_name = "lms"

    @property
    def viewsets(self):  # type: ignore[override]
        # Lazy imports to avoid circular dependencies at module load time
        from www.apps.lms.components import CourseListFragment, DashboardComponent
        from www.apps.lms.viewsets import CourseViewset, EnrollmentViewset
        return [
            DashboardComponent(),
            CourseViewset(),
            EnrollmentViewset(),
            CourseListFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated and user.is_staff


# ---------------------------------------------------------------------------
# Blog Application
# ---------------------------------------------------------------------------

class BlogApp(Application):
    """Blog — public read, staff write."""

    title = "Blog"
    icon = "article"
    app_name = "blog"

    @property
    def viewsets(self):  # type: ignore[override]
        from www.apps.blog.components import BlogPostCreateFragment, BlogPostListFragment
        from www.apps.blog.viewsets import BlogCategoryViewset, BlogPostViewset
        return [
            BlogPostViewset(),
            BlogCategoryViewset(),
            BlogPostListFragment(),
            BlogPostCreateFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return True  # Public


# ---------------------------------------------------------------------------
# Site
# ---------------------------------------------------------------------------

site = Site(
    title="CTC Research",
    viewsets=[
        LMSApp(),
        BlogApp(),
    ],
)
