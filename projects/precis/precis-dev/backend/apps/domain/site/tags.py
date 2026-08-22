"""
domain.site.tags
=================================

Re-exports from django_fusion.contrib.views for backward compatibility.
"""
from django_fusion.routes.tags import EnhancedTagsView  # noqa: F401

__all__ = ["EnhancedTagsView"]

