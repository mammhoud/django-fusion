"""
CTC Research — Routable Components Site Configuration
======================================================

Defines the Application and Site hierarchy for the routable-components
routing system. Coexists with the existing manual URL routing in apps/urls.py.

Wire into projects/urls.py::

    from www.core.routes import site
    urlpatterns += [path("osoul/", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))]

Generated URL prefix: /osoul/
  /osoul/lms/dashboard/
  /osoul/lms/courses/list-fragment/   (HTMX only)
  /osoul/blog/posts/list-fragment/    (HTMX only)
  /osoul/blog/posts/create-fragment/  (HTMX only)
"""

from __future__ import annotations

from django_fusion.routes import Application, Site, viewprop

# ---------------------------------------------------------------------------
# LMS Application
# ---------------------------------------------------------------------------

class LMSApp(Application):
    """Learning Management System — staff only."""

    title = "Learning"
    icon = "school"
    app_name = "lms"

    @viewprop
    def viewsets(self):
        # Lazy import to avoid circular dependencies during module load
        from plugins.lms.components import (
            CourseListFragment,
            DashboardComponent,
            PrivacyPageFragment,
            StaticPageFragment,
        )
        from plugins.lms.viewsets import CourseViewset, EnrollmentViewset
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

    @viewprop
    def viewsets(self):
        from plugins.blog.components import BlogPostCreateFragment, BlogPostListFragment
        from plugins.blog.viewsets import BlogCategoryViewset, BlogPostViewset
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

# -----------------------------------------------------------------------
# Backwards-compatible site variable
# The actual Site instance is created lazily in get_site() to avoid
# circular import issues during module load time when models are imported
# before Django is fully initialized.
# -----------------------------------------------------------------------
_site = None


def get_site():
    """Lazy site creation - ensures Django is initialized before model imports."""
    global _site
    if _site is None:
        _site = Site(
            title="CTC Research",
            viewsets=[
                LMSApp(),
                BlogApp(),
            ],
        )
    return _site


# For backwards compatibility, expose as 'site' but it's actually lazy
site = get_site()

# ---------------------------------------------------------------------------
# Lazy site creation to avoid circular imports during module load
# ---------------------------------------------------------------------------

_site = None


def get_site():
    """Lazy site creation to ensure Django is initialized before model imports."""
    global _site
    if _site is None:
        _site = Site(
            title="CTC Research",
            viewsets=[
                LMSApp(),
                BlogApp(),
            ],
        )
    return _site


# Keep 'site' for backwards compatibility, but use the lazy version
site = get_site()
