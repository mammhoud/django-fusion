"""
Utility re-exports from django_osoul.site.

This module provides re-exports of utility functions from django_osoul.site
for backward compatibility and convenience.

Functions:
    unique_ordered: Return items with duplicates removed, preserving order.

Usage::

    from django_osoul.contrib.utils import unique_ordered
"""

from django_osoul.site.utils import unique_ordered

__all__ = ["unique_ordered"]
