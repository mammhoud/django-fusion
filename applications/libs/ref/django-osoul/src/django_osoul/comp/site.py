"""
django_osoul.comp.site - Legacy import shim

This module provides backward compatibility for imports from django_osoul.comp.site.*
The actual code has been moved to django_osoul.site.*
"""
import warnings

# Re-export from django_osoul.site
from django_osoul.site import (  # noqa: F401
    HtmxDetails,
    HttpResponseClientRedirect,
    HttpResponseStopPolling,
    NotificationMixin,
    PageHandler,
)
from django_osoul.site.generic import (  # noqa: F401
    Action,
    CreateModelView,
    DeleteBulkActionView,
    DeleteModelView,
    DetailModelView,
    ListModelView,
    UpdateModelView,
)

warnings.warn(
    "django_osoul.comp.site has been moved to django_osoul.site. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
