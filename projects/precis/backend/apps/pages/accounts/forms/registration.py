"""
Registration Forms
==================
Secure forms for user registration and password creation.
"""

import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrationForm(forms.Form):
    """
    Registration form: collects full name and email.
    User is created as inactive until they set their password.
    """

    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Full Name"),
                "class": "form-input",
                "autocomplete": "name",
                "id": "id_full_name",
            }
        ),
        label=_("Full Name"),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": _("Email Address"),
                "class": "form-input",
                "autocomplete": "email",
                "id": "id_email",
            }
        ),
        label=_("Email Address"),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                _("An account with this email address already exists.")
            )
        return email

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if len(name) < 2:
            raise ValidationError(_("Please enter your full name."))
        # Basic sanitization
        name = re.sub(r'[<>{}[\]\\]', '', name)
        return name


class PasswordCreationForm(forms.Form):
    """
    Password creation form for users activating their account.
    Enforces strong password policy.
    """

    password = forms.CharField(
        min_length=8,
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Create Password"),
                "class": "form-input",
                "autocomplete": "new-password",
                "id": "id_password",
            }
        ),
        label=_("Password"),
    )
    password_confirm = forms.CharField(
        min_length=8,
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Confirm Password"),
                "class": "form-input",
                "autocomplete": "new-password",
                "id": "id_password_confirm",
            }
        ),
        label=_("Confirm Password"),
    )

    def clean_password(self):
        password = self.cleaned_data["password"]
        errors = []

        if len(password) < 8:
            errors.append(_("Password must be at least 8 characters long."))
        if not re.search(r'[A-Z]', password):
            errors.append(_("Password must contain at least 1 uppercase letter."))
        if not re.search(r'[a-z]', password):
            errors.append(_("Password must contain at least 1 lowercase letter."))
        if not re.search(r'[0-9]', password):
            errors.append(_("Password must contain at least 1 number."))
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append(_("Password must contain at least 1 special character."))

        if errors:
            raise ValidationError(errors)

        # Run Django's built-in validators too
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError(
                {"password_confirm": _("Passwords do not match.")}
            )

        return cleaned_data
