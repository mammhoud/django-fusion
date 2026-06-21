"""
django_rseal.pipelines - Legacy import shim

This module provides backward compatibility for imports from django_rseal.workflows.pipelines.*
The actual code has been moved to django_rseal.models.*
"""
import warnings

warnings.warn(
    "django_rseal.pipelines has been moved to django_rseal.models. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
