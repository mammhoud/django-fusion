"""
django_fusion.comp.forms — Form utilities and mixins.

This module provides form classes and mixins for django-fusion component forms.
Note: Most functionality has been moved to HTMX handlers and form handlers.

Classes:
    LayoutElement: Base class for form layout elements.
    FormAjaxCompleteMixin: Stub mixin (functionality moved to HTMX handlers).
    FormDependentSelectMixin: Stub mixin (functionality moved to form handlers).

Deprecated:
    This module is deprecated. Use django.forms.ModelForm directly.
"""
import warnings

# Re-export stubs from the sibling forms.py for backward compat
from django import forms as _dj_forms

from .layout import LayoutElement  # noqa: F401

ModelForm = _dj_forms.ModelForm


class FormAjaxCompleteMixin:
    """Stub mixin - functionality moved to HTMX handlers."""
    pass


class FormDependentSelectMixin:
    """Stub mixin - functionality moved to form handlers."""
    pass


warnings.warn(
    "django_fusion.comp.forms has been deprecated. "
    "Use django.forms.ModelForm directly.",
    DeprecationWarning,
    stacklevel=2,
)
