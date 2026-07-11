"""VResume error tracker — delegates to django_fusion."""
from django_fusion.core.middlewares.error_tracker import ErrorTrackerMiddleware

__all__ = ["ErrorTrackerMiddleware"]
