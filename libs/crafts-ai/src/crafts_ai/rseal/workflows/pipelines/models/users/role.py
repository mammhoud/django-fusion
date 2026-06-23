"""
crafts_ai.pipelines.models.users.role - Legacy import shim

This module provides backward compatibility for imports from crafts_ai.workflows.pipelines.models.users.role.*
The actual code has been moved to crafts_ai.email.models.models.*
"""
import warnings

warnings.warn(
    "crafts_ai.pipelines.models.users.role has been moved to crafts_ai.email.models.models. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from crafts_ai.communication.email.models.models import UserRole  # noqa: F401

__all__ = ["UserRole"]
