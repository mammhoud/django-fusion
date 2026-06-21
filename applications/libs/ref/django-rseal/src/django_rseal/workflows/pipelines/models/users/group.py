"""
django_rseal.pipelines.models.users.group - Legacy import shim

This module provides backward compatibility for imports from django_rseal.workflows.pipelines.models.users.group.*
The actual code has been moved to django_rseal.models.users.*
"""
import warnings

warnings.warn(
    "django_rseal.pipelines.models.users.group has been moved to django_rseal.models.users. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from django_rseal.content.models.users import UserGroup  # noqa: F401

__all__ = ["UserGroup"]
