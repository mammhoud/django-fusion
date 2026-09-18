"""
Blog Application for precis-lms.com
=====================================

Defines the ``BlogApp`` Application (routable-components hierarchy node)
for the Blog. Kept in the blog app so core routing only assembles the
``Module`` from app-level Application classes.

Usage (in core/routes.py)::

    from apps.pages.blog.application import BlogApp

    module = Module(title="LMS Fusion", viewsets=[LMSApp(), BlogApp()])
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.core.base import viewprop
from django_fusion.routes.core.sites import Application


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

    # No Wagtail ``BlogPage`` exists in the fixture set, so the inherited
    # ``index_path`` would 302 ``/blog/`` to the staff-only routable
    # BlogPostViewset list (``/blog/blogpost/`` → sign-in wall) — matching
    # LMS, ``/blog/`` is left to fall through to Wagtail (404). ``index_path
    # = None`` removes the inherited pattern (ViewsetMeta) while the HTMX
    # action fragments (``/blog/posts/``, ``/blog/posts/list-fragment/``,
    # ``/blog/posts/create-fragment/``) stay mounted.
    index_path = None

    @viewprop
    def viewsets(self):
        from apps.pages.blog.components import (
            ActionBlogPostListFragment,
            BlogPostCreateFragment,
            BlogPostListFragment,
        )
        from apps.pages.blog.viewsets import BlogCategoryViewset, BlogPostViewset
        return [
            BlogPostViewset(),
            BlogCategoryViewset(),
            BlogPostListFragment(),
            ActionBlogPostListFragment(),
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


__all__ = ["BlogApp"]
