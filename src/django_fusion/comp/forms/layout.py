"""
django_fusion.comp.forms.layout - Legacy import shim
"""
import os
import warnings

class LayoutElement:
    """Stub class - functionality moved to form layouts."""
    pass

# Gated deprecation warning — see comp/forms/__init__.py docstring for
# the rationale on `DJANGO_FUSION_QUIET_DEPRECATION`. Both stub modules
# gate on the same env var so the regression suite can opt out
# deterministically; production users always see the signal.
if not os.environ.get("DJANGO_FUSION_QUIET_DEPRECATION"):
    warnings.warn(
        "django_fusion.comp.forms.layout has been deprecated.",
        DeprecationWarning,
        stacklevel=2,
    )
