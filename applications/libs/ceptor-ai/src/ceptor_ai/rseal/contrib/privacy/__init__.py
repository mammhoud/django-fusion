"""Privacy utilities - shim re-exporting from django_osoul."""
import warnings

from django_osoul.contrib.privacy import *  # noqa: F401, F403

__all__ = []

warnings.warn(
    "ceptor_ai.contrib.privacy has been moved to django_osoul.contrib.privacy. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
