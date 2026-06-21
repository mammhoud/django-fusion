"""Admin integration - shim re-exporting from django_osoul."""
import warnings

from django_osoul.contrib.admin import *  # noqa: F401, F403

__all__ = []

warnings.warn(
    "django_rseal.contrib.admin has been moved to django_osoul.contrib.admin. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
