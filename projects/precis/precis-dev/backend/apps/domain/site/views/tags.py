"""
Tags views.

Re-exports from django_fusion.contrib.views.tags for backward compatibility.

Canonical import: from django_fusion.contrib.views import TagsView
"""

from django_fusion.routes.tags import EnhancedTagsView as TagsView  # noqa: F401

__all__ = ["TagsView"]
