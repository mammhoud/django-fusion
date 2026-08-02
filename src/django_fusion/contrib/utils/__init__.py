"""
Utility re-exports from django_fusion.routes.

This module provides re-exports of utility functions from django_fusion.routes
for backward compatibility and convenience.

Functions:
    unique_ordered: Return items with duplicates removed, preserving order.

Usage::

    from django_fusion.contrib.utils import unique_ordered
"""

from django_fusion.core.utils import unique_ordered

__all__ = ["unique_ordered"]
