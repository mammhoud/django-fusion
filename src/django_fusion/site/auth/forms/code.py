"""
Code-based authentication forms for login verification.
"""

from allauth.account import app_settings
from allauth.account.app_settings import LoginMethod
from allauth.account.utils import filter_users_by_email, get_adapter
from allauth.core import context, ratelimit
from django import forms
from django.utils.translation import gettext_lazy as _

from django_fusion.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin


class RequestLoginCodeForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                          ValidationMixin, forms.Form):
    """
    Form for requesting login codes via email or phone.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": _("Email address"), "autocomplete": "email"}
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._has_email = LoginMethod.EMAIL in app_settings.LOGIN_METHODS
        self._has_phone = LoginMethod.PHONE in app_settings.LOGIN_METHODS

        if self._has_phone:
            adapter = get_adapter()
            self.fields["phone"] = adapter.phone_form_field(required=not self._has_email)

        if self._has_phone and not self._has_email:
            self.fields.pop("email")

        # Setup form layout
        fields = []
        if self._has_email:
            fields.append("email")
        if self._has_phone:
            fields.append("phone")

        self.setup_layout(
            fields=fields,
            submit_text=_("Send Code"),
            show_links=True
        )

        # Apply styling
        if 'email' in self.fields:
            self.apply_field_styling(
                self.fields['email'],
                field_type='email',
                placeholder=_("Email address")
            )

        if 'phone' in self.fields:
            self.apply_field_styling(
                self.fields['phone'],
                field_type='tel',
                placeholder=_("Phone number")
            )

    def clean(self):
        cleaned_data = super().clean()
        adapter = get_adapter()
        phone = cleaned_data.get("phone")
        email = cleaned_data.get("email")

        if email and phone:
            raise adapter.validation_error("select_only_one")
        return cleaned_data

    def clean_phone(self):
        adapter = get_adapter()
        phone = self.cleaned_data["phone"]
        if phone:
            self._user = adapter.get_user_by_phone(phone)
            if not self._user and not app_settings.PREVENT_ENUMERATION:
                raise adapter.validation_error("unknown_phone")
            if not ratelimit.consume(context.request, "request_login_code", key=phone.lower()):
                raise adapter.validation_error("too_many_login_attempts")
        return phone

    def clean_email(self):
        adapter = get_adapter()
        email = self.cleaned_data["email"]
        users = filter_users_by_email(email, is_active=True, prefer_verified=True)
        if not users and not app_settings.PREVENT_ENUMERATION:
            raise adapter.validation_error("unknown_email")
        if not ratelimit.consume(context.request, "request_login_code", key=email.lower()):
            raise adapter.validation_error("too_many_login_attempts")
        self._user = users[0] if users else None
        return email


class VerifyCodeForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                    ValidationMixin, forms.Form):
    """
    Form for verifying login codes.
    """

    code = forms.CharField(
        label=_("Verification code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": _("Enter 6-digit code"),
            "autocomplete": "one-time-code",
            "inputmode": "numeric",
            "pattern": "[0-9]*",
        }),
        help_text=_("Enter the 6-digit code sent to your email or phone."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["code"],
            submit_text=_("Verify Code"),
            show_links=False
        )

        # Apply styling
        self.apply_field_styling(
            self.fields['code'],
            field_type='text',
            placeholder=_("Enter verification code")
        )
