"""
domain.site.tags
=================================

Re-exports from django_fusion.contrib.views for backward compatibility.
"""
from django_fusion.site.interface.views.tags import EnhancedTagsView  # noqa: F401

__all__ = ["EnhancedTagsView"]

