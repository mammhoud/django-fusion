"""
django_rseal.pipelines.models.users.role - Legacy import shim

This module provides backward compatibility for imports from django_rseal.workflows.pipelines.models.users.role.*
The actual code has been moved to django_rseal.email.models.models.*
"""
import warnings

warnings.warn(
    "django_rseal.pipelines.models.users.role has been moved to django_rseal.email.models.models. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from django_rseal.communication.email.models.models import UserRole  # noqa: F401

__all__ = ["UserRole"]
