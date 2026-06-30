"""
ceptor_ai.pipelines.models.default - Legacy import shim
"""
import warnings

from ceptor_ai.content.models.default import DefaultBase  # noqa: F401

warnings.warn(
    "ceptor_ai.pipelines.models.default has been moved to ceptor_ai.models.default. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DefaultBase"]
