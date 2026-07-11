"""Backward-compatible registration forms without importing account-wide forms."""

import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("An account with this email address already exists."))
        return email

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if len(name) < 2:
            raise ValidationError(_("Please enter your full name."))
        return re.sub(r'[<>{}[\]\\]', '', name)


class PasswordCreationForm(forms.Form):
    password = forms.CharField(min_length=8, max_length=128, widget=forms.PasswordInput)
    password_confirm = forms.CharField(min_length=8, max_length=128, widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data["password"]
        errors = []
        if len(password) < 8:
            errors.append(_("Password must be at least 8 characters long."))
        if not re.search(r"[A-Z]", password):
            errors.append(_("Password must contain at least 1 uppercase letter."))
        if not re.search(r"[a-z]", password):
            errors.append(_("Password must contain at least 1 lowercase letter."))
        if not re.search(r"[0-9]", password):
            errors.append(_("Password must contain at least 1 number."))
        if not re.search(r'''[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]''', password):
            errors.append(_("Password must contain at least 1 special character."))
        if errors:
            raise ValidationError(errors)
        try:
            validate_password(password)
        except ValidationError as exc:
            raise ValidationError(exc.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise ValidationError({"password_confirm": _("Passwords do not match.")})
        return cleaned_data


__all__ = ["PasswordCreationForm", "RegistrationForm"]
