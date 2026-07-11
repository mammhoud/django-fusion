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
import os
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


# Gated deprecation warning: the regression suite sets
# `DJANGO_FUSION_QUIET_DEPRECATION=1` in conftest.py BEFORE importing
# Django (which is what loads this module via INSTALLED_APPS).  Production
# users never have this env var set, so the warning surfaces normally;
# pytest invocations of the regression suite run silent.  Setting this
# gate here (rather than via conftest-side `warnings.filterwarnings`) is
# deterministic across pytest versions and avoids every catch-warnings /
# pytest-configure-ordering footgun we hit before (see conftest.py
# section 2 commentary for the iteration history).
if not os.environ.get("DJANGO_FUSION_QUIET_DEPRECATION"):
    warnings.warn(
        "django_fusion.comp.forms has been deprecated. "
        "Use django.forms.ModelForm directly.",
        DeprecationWarning,
        stacklevel=2,
    )
