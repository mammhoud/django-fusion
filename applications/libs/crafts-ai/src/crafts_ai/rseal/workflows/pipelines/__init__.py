"""
crafts_ai.pipelines - Legacy import shim

This module provides backward compatibility for imports from crafts_ai.workflows.pipelines.*
The actual code has been moved to crafts_ai.models.*
"""
import warnings

warnings.warn(
    "crafts_ai.pipelines has been moved to crafts_ai.models. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
