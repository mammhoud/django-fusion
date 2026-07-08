"""
Enhanced code confirmation forms with dual-framework styling.
Includes login code, email verification, and password reset code confirmation.
"""

from allauth.account.internal.flows.manage_email import email_already_exists
from allauth.core.internal.cryptokit import compare_user_code as compare_code
from allauth.account.adapter import get_adapter
from django import forms
from django.utils.translation import gettext_lazy as _

from django_fusion.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin


class BaseConfirmCodeForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                         ValidationMixin, forms.Form):
    """
    Base form for code confirmation with enhanced styling support.
    """

    code = forms.CharField(
        label=_("Verification Code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Enter 6-digit code"),
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
            }
        ),
        help_text=_("Enter the verification code sent to your email or phone."),
    )

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop("code", None)
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["code"],
            submit_text=self.get_submit_text(),
            show_links=False
        )

        # Apply styling
        self.apply_field_styling(
            self.fields['code'],
            field_type='text',
            placeholder=_("Enter 6-digit code")
        )

    def get_submit_text(self):
        """Get the submit button text."""
        return _("Verify Code")

    def clean_code(self):
        """Validate the verification code."""
        code = self.cleaned_data.get("code")
        if not compare_code(actual=code, expected=self.code):
            adapter = get_adapter()
            if self.style_framework == 'tailwind':
                error_msg = _("The verification code is incorrect. Please try again.")
            else:
                error_msg = adapter.validation_error("incorrect_code")
            raise forms.ValidationError(error_msg)
        return code


class EnhancedConfirmLoginCodeForm(BaseConfirmCodeForm):
    """
    Enhanced form for confirming login verification codes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].label = _("Login Verification Code")
        self.fields['code'].help_text = _(
            "Enter the 6-digit verification code sent to your email or phone to complete login."
        )


class EnhancedConfirmEmailVerificationCodeForm(BaseConfirmCodeForm):
    """
    Enhanced form for confirming email verification codes.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.email = kwargs.pop("email", None)
        super().__init__(*args, **kwargs)

        self.fields['code'].label = _("Email Verification Code")
        self.fields['code'].help_text = _(
            "Enter the 6-digit verification code sent to your email address."
        )

    def get_submit_text(self):
        """Get the submit button text."""
        return _("Verify Email")

    def clean_code(self):
        """Validate email verification code."""
        code = super().clean_code()
        if code:
            # Check if email already exists for another user
            email_already_exists(user=self.user, email=self.email, always_raise=True)
        return code


class EnhancedConfirmPasswordResetCodeForm(BaseConfirmCodeForm):
    """
    Enhanced form for confirming password reset codes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].label = _("Password Reset Code")
        self.fields['code'].help_text = _(
            "Enter the 6-digit verification code sent to your email to reset your password."
        )

    def get_submit_text(self):
        """Get the submit button text."""
        return _("Reset Password")
