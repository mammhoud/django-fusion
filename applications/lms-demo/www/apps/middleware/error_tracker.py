"""
ErrorTrackerMiddleware

This module re-exports ErrorTrackerMiddleware from django_osoul.
Delegates to django_osoul.handlers.ErrorTrackerMiddleware.
"""

from django_osoul.core.handlers import ErrorTrackerMiddleware

__all__ = ["ErrorTrackerMiddleware"]
