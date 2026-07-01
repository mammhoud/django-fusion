"""Compatibility shim — ``django_osoul.cache`` is now ``django_osoul.core.cache``.

Import from the canonical path instead::

    from django_osoul.core.cache import CachedManager, CachedModelManager
"""
from __future__ import annotations
from django_osoul.core.cache import CachedManager, CachedModelManager  # noqa: F401

__all__ = ["CachedManager", "CachedModelManager"]
