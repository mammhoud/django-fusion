"""Privacy utilities - shim re-exporting from django_fusion."""
import warnings

from django_fusion.contrib.privacy import *  # noqa: F401, F403

__all__ = []

warnings.warn(
    "ceptor_ai.contrib.privacy has been moved to django_fusion.contrib.privacy. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
