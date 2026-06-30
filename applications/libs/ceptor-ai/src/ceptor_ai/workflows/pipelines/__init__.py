"""
ceptor_ai.pipelines - Legacy import shim

This module provides backward compatibility for imports from ceptor_ai.workflows.pipelines.*
The actual code has been moved to ceptor_ai.models.*
"""
import warnings

warnings.warn(
    "ceptor_ai.pipelines has been moved to ceptor_ai.models. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
