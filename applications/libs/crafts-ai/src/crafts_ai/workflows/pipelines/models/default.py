"""
crafts_ai.pipelines.models.default - Legacy import shim
"""
import warnings

from crafts_ai.content.models.default import DefaultBase  # noqa: F401

warnings.warn(
    "crafts_ai.pipelines.models.default has been moved to crafts_ai.models.default. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DefaultBase"]
