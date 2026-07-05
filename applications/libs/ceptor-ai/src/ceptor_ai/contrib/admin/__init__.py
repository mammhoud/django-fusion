"""Admin integration - shim re-exporting from django_fusion."""
import warnings

from django_fusion.contrib.admin import *  # noqa: F401, F403

__all__ = []

warnings.warn(
    "ceptor_ai.contrib.admin has been moved to django_fusion.contrib.admin. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
