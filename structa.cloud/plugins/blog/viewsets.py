"""
Blog Viewsets for structa.cloud
=====================================

Routable ModelViewsets for the Blog application.
These work alongside the existing URL definitions in apps/blog/urls.py.

Usage::

    from plugins.blog.viewsets import BlogPostViewset
    # Register in apps/core/routes.py → BlogApp.viewsets
"""

from __future__ import annotations

from django_osoul.web.routes import ModelViewset


class BlogPostViewset(ModelViewset):
    """
    Full CRUD interface for blog posts.

    Generates:
      GET  /osoul/blog/posts/              → list
      GET  /osoul/blog/posts/add/          → create form
      GET  /osoul/blog/posts/<pk>/detail/  → detail
      GET  /osoul/blog/posts/<pk>/change/  → update form
      GET  /osoul/blog/posts/<pk>/delete/  → delete confirm
    """

    icon = "article"

    @property
    def model(self):
        from apps.blog.models import BlogPost
        return BlogPost

    list_columns = ("title", "author", "published_date", "status")
    list_filter_fields = ("status",)
    list_search_fields = ("title", "content")

    def has_view_permission(self, user, obj=None):
        return True  # Public list/detail

    def has_add_permission(self, user):
        return user.has_perm("blog.add_blogpost")

    def has_change_permission(self, user, obj=None):
        return user.has_perm("blog.change_blogpost")

    def has_delete_permission(self, user, obj=None):
        return user.has_perm("blog.delete_blogpost")


class BlogCategoryViewset(ModelViewset):
    """CRUD for blog categories (staff only)."""

    icon = "label"

    @property
    def model(self):
        from apps.blog.models import BlogCategory
        return BlogCategory

    list_columns = ("name", "slug")
    list_search_fields = ("name",)

    def has_view_permission(self, user, obj=None):
        return user.is_staff

    def has_add_permission(self, user):
        return user.is_staff

    def has_change_permission(self, user, obj=None):
        return user.is_staff

    def has_delete_permission(self, user, obj=None):
        return user.is_staff
