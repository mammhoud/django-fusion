"""Email configuration utilities - shim re-exporting from django_osoul."""
import warnings

from django_osoul.contrib.email_config import *  # noqa: F401, F403

__all__ = []

warnings.warn(
    "django_rseal.contrib.email_config has been moved to django_osoul.contrib.email_config. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
