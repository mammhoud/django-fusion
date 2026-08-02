"""
Blog Application for fusion-cms.com
=====================================

Defines the ``BlogApp`` Application (routable-components hierarchy node)
for the Blog. Kept in the blog app so core routing only assembles the
``Site`` from app-level Application classes.

Usage (in core/routes.py)::

    from apps.pages.blog.application import BlogApp

    site = Site(title="Fusion CMS", viewsets=[LMSApp(), BlogApp()])
"""

from __future__ import annotations

from django_fusion.routes.core.sites import Application
from django_fusion.routes.core.base import viewprop


class BlogApp(Application):
    """Blog — public read, staff write."""

    title = "Blog"
    icon = "article"
    app_name = "blog"

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

    def has_view_permission(self, user, obj=None):
        return True  # Public


__all__ = ["BlogApp"]
