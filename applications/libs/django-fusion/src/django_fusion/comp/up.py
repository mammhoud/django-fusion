"""
django_fusion.comp.up - Legacy import shim
"""
import warnings

class Unpoly:
    """Stub class - functionality moved to site middleware."""
    pass

warnings.warn(
    "django_fusion.comp.up has been moved. Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
