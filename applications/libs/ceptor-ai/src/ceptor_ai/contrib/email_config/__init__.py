"""Email configuration utilities - shim re-exporting from django_fusion."""
import warnings

from django_fusion.contrib.email_config import *  # noqa: F401, F403

__all__ = []

warnings.warn(
    "ceptor_ai.contrib.email_config has been moved to django_fusion.contrib.email_config. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
