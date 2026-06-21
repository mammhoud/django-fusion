"""
crafts_ai.pipelines.models.users.group - Legacy import shim

This module provides backward compatibility for imports from crafts_ai.workflows.pipelines.models.users.group.*
The actual code has been moved to crafts_ai.models.users.*
"""
import warnings

warnings.warn(
    "crafts_ai.pipelines.models.users.group has been moved to crafts_ai.models.users. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from crafts_ai.content.models.users import UserGroup  # noqa: F401

__all__ = ["UserGroup"]
