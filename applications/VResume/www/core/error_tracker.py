"""VResume error tracker — delegates to django_osoul."""
from django_osoul.core.middlewares.error_tracker import ErrorTrackerMiddleware

__all__ = ["ErrorTrackerMiddleware"]
