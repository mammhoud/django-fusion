"""
django_fusion.comp.adapters - Legacy import shim
"""
import warnings

class DjangoAdapter:
    """Stub adapter - functionality moved to site adapters."""
    pass

warnings.warn(
    "django_fusion.comp.adapters has been moved. Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
