"""
ErrorTrackerMiddleware

This module re-exports ErrorTrackerMiddleware from django_fusion.
Delegates to django_fusion.handlers.ErrorTrackerMiddleware.
"""

from django_fusion.core.handlers import ErrorTrackerMiddleware

__all__ = ["ErrorTrackerMiddleware"]
