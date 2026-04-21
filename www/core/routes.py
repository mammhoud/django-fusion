"""
Structa Cloud — Routable Components Site Configuration
=======================================================

Defines the Application and Site hierarchy for the routable-components
routing system. Coexists with the existing manual URL routing in apps/urls.py.

Wire into core/urls.py::

    from www.apps.core.routes import site
    urlpatterns += [path("osoul/", include(site.urls))]

Generated URL prefix: /osoul/
  /osoul/blog/posts/list-fragment/    (HTMX only)
  /osoul/blog/posts/create-fragment/  (HTMX only)
"""

from __future__ import annotations

from django_osoul.routes import Application, Site, viewprop

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
    title="Structa Cloud",
    viewsets=[
        BlogApp(),
    ],
)
