"""
Django admin configuration for handlers app.
"""

from .tags import TagAdmin, TaggedItemAdmin

__all__ = ['TagAdmin', 'TaggedItemAdmin']
