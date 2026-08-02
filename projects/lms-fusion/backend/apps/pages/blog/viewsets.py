"""
Blog Viewsets for fusion-cms.com
=====================================

Routable ModelViewsets for the Blog application.
These replace manual URL definitions in apps/blog/urls.py for the
new routable-components routing system.

Usage::

    from apps.pages.blog.viewsets import BlogPostViewset
    # Register in apps/projects/routes.py → BlogApp.viewsets
"""

from __future__ import annotations

from django_fusion.routes.models.crud import ModelViewset


class BlogPostViewset(ModelViewset):
    """
    Full CRUD interface for blog posts.

    Generates:
      GET  /app/blog/posts/              → list
      GET  /app/blog/posts/add/          → create form
      GET  /app/blog/posts/<pk>/detail/  → detail
      GET  /app/blog/posts/<pk>/change/  → update form
      GET  /app/blog/posts/<pk>/delete/  → delete confirm
    """

    icon = "article"

    @property
    def model(self):
        from apps.pages.blog.models import BlogPost
        return BlogPost

    list_columns = ("title", "author", "category", "published_date", "status")
    list_filter_fields = ("category", "status")
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
        from apps.pages.blog.models import BlogCategory
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
