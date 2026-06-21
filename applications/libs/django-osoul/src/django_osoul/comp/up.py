"""
django_osoul.comp.up - Legacy import shim
"""
import warnings

class Unpoly:
    """Stub class - functionality moved to site middleware."""
    pass

warnings.warn(
    "django_osoul.comp.up has been moved. Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
