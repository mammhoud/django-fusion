"""
Form Validators
===============
Reusable Django form/serializer validators.

Usage::

    from django_fusion.core.filters import UniqueFieldValidator, SlugFieldValidator

    class MyForm(forms.Form):
        username = forms.CharField(
            validators=[UniqueFieldValidator(User, "username")]
        )
        slug = forms.SlugField(
            validators=[SlugFieldValidator()]
        )
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UniqueFieldValidator:
    """Raise ``ValidationError`` if *value* already exists in the queryset.

    Args:
        queryset_or_model: A Django queryset **or** a model class.  When a
            model class is given, ``Model.objects.all()`` is used.
        field_name: The model field to check for uniqueness.
        message: Custom error message.  Defaults to a generic uniqueness
            message.
    """

    def __init__(self, queryset_or_model, field_name: str, message: str | None = None) -> None:
        from django.db import models as _models

        if isinstance(queryset_or_model, type) and issubclass(queryset_or_model, _models.Model):
            self.queryset = queryset_or_model.objects.all()
        else:
            self.queryset = queryset_or_model

        self.field_name = field_name
        self.message = message or _("This value already exists.")

    def __call__(self, value) -> None:
        if self.queryset.filter(**{self.field_name: value}).exists():
            raise ValidationError(self.message)


class SlugFieldValidator:
    """Validate that *value* is a valid slug (lowercase, alphanumeric, hyphens).

    Optionally also checks uniqueness against a queryset.

    Args:
        queryset: Optional queryset to check uniqueness against.  The field
            name used for the lookup is ``"slug"``.
        message: Custom error message for format failures.
    """

    _SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def __init__(self, queryset=None, message: str | None = None) -> None:
        self.queryset = queryset
        self.message = message or _("Enter a valid slug (lowercase letters, numbers, and hyphens).")

    def __call__(self, value) -> None:
        if not self._SLUG_RE.match(value):
            raise ValidationError(self.message)

        if self.queryset is not None and self.queryset.filter(slug=value).exists():
            raise ValidationError(_("This slug is already in use."))
