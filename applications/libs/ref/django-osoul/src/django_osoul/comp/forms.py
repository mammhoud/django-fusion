"""
django_osoul.comp.forms - Legacy import shim

This module provides backward compatibility for imports from django_osoul.comp.forms.*
The actual code has been moved to django_osoul.forms or django.forms.
"""
import warnings
from django import forms

# Use Django's ModelForm directly
ModelForm = forms.ModelForm

# Stub mixins for backward compatibility
class FormAjaxCompleteMixin:
    """Stub mixin - functionality moved to HTMX handlers."""
    pass

class FormDependentSelectMixin:
    """Stub mixin - functionality moved to form handlers."""
    pass

class LayoutElement:
    """Stub class - functionality moved to form layouts."""
    pass

warnings.warn(
    "django_osoul.comp.forms has been deprecated. "
    "Use django.forms.ModelForm directly.",
    DeprecationWarning,
    stacklevel=2,
)
