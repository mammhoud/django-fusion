"""Compatibility shim — ``django_osoul.middlewares`` is now ``django_osoul.core.middlewares``.

Import from the canonical path instead::

    from django_osoul.core.middlewares.error_tracker import ErrorTrackerMiddleware
    from django_osoul.core.middlewares.privacy import PrivacyMiddleware
    from django_osoul.core.middlewares.language import LanguageMiddleware
"""
from __future__ import annotations
from django_osoul.core.middlewares.error_tracker import ErrorTrackerMiddleware  # noqa: F401

__all__ = ["ErrorTrackerMiddleware"]
