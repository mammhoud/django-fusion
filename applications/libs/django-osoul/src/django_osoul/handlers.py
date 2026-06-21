"""Backward-compatible imports for legacy django_osoul.handlers users."""

from django_osoul.middlewares.error_tracker import ErrorTrackerMiddleware

__all__ = ["ErrorTrackerMiddleware"]
