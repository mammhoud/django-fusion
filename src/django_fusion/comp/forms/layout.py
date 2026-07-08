"""
django_fusion.comp.forms.layout - Legacy import shim
"""
import warnings

class LayoutElement:
    """Stub class - functionality moved to form layouts."""
    pass

warnings.warn(
    "django_fusion.comp.forms.layout has been deprecated.",
    DeprecationWarning,
    stacklevel=2,
)
