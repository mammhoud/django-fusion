"""
django_rseal.pipelines.models.default - Legacy import shim
"""
import warnings

from django_rseal.content.models.default import DefaultBase  # noqa: F401

warnings.warn(
    "django_rseal.pipelines.models.default has been moved to django_rseal.models.default. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DefaultBase"]
