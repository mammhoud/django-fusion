"""
django_osoul.middlewares — generic Django middleware.

Canonical imports::

    from django_osoul.core.middlewares import ErrorTrackerMiddleware
    from django_osoul.core.middlewares import SiteMiddleware
    from django_osoul.core.middlewares import DefaultLanguageMiddleware
    from django_osoul.core.middlewares import ReadonlyExceptionHandlerMiddleware

Settings usage::

    MIDDLEWARE = [
        "django_osoul.middlewares.error_tracker.ErrorTrackerMiddleware",
        "django_osoul.middlewares.site.SiteMiddleware",
    ]
"""
from .error_tracker import ErrorTrackerMiddleware  # noqa: F401
from .freeze import ReadonlyExceptionHandlerMiddleware  # noqa: F401
from .language import DefaultLanguageMiddleware  # noqa: F401
from .site import SiteMiddleware  # noqa: F401
