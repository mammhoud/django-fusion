"""Canonical fragment rendering context exports.

The implementation is maintained in ``_context_mixins``; this module keeps a
stable, explicit import path for callers that need the fragment handler.
"""

from django_fusion.core.context._context_mixins import FragmentHandlerMixin

__all__ = ["FragmentHandlerMixin"]
