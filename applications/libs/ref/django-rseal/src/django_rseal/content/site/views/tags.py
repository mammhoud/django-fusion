"""
Tags views.

Re-exports from django_osoul.contrib.views.tags for backward compatibility.

Canonical import: from django_osoul.contrib.views import TagsView
"""

from django_osoul.site.views.tags import EnhancedTagsView as TagsView  # noqa: F401

__all__ = ["TagsView"]
