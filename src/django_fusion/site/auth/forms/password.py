"""
 password forms with dual-framework styling.
Includes password reset, change, and set password forms.
"""

from allauth.account import app_settings
from allauth.account.forms import default_token_generator
from allauth.account.internal import flows
from allauth.account.utils import filter_users_by_email, get_adapter
from crispy_forms.layout import HTML
from django import forms
from django.contrib.auth import password_validation
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_fusion.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin, PasswordVerificationMixin

# -------------------------------------------------------------------------
# PASSWORD FIELD CLASSES
# -------------------------------------------------------------------------

class PasswordField(forms.CharField):
    """ password field with dual-framework styling support."""

    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop(
            "render_value", app_settings.PASSWORD_INPUT_RENDER_VALUE
        )

        # Create widget with initial attributes
        widget = forms.PasswordInput(
            render_value=render_value,
            attrs={
                "placeholder": kwargs.get("label"),
                "class": "form-control",  # Base class, will be overridden
            }
        )

        # Add autocomplete if specified
        autocomplete = kwargs.pop("autocomplete", None)
        if autocomplete is not None:
            widget.attrs["autocomplete"] = autocomplete

        kwargs["widget"] = widget
        super().__init__(*args, **kwargs)


class SetPasswordField(PasswordField):
    """ set password field with validation."""

    def __init__(self, *args, **kwargs):
        kwargs["autocomplete"] = "new-password"
        kwargs.setdefault(
            "help_text", password_validation.password_validators_help_text_html()
        )
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self, value):
        """Clean and validate password."""
        value = super().clean(value)
        if value:
            value = get_adapter().clean_password(value, user=self.user)
        return value


# -------------------------------------------------------------------------
# PASSWORD VERIFICATION MIXIN
# -------------------------------------------------------------------------

class PasswordVerificationMixin:
    """
    Mixin for forms that require password verification (two password fields).
    """

    def clean(self):
        """Validate that both password fields match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("Passwords do not match. Please enter the same password in both fields."))

        return cleaned_data


# -------------------------------------------------------------------------
# PASSWORD CHANGE FORM
# -------------------------------------------------------------------------

class ChangePasswordForm(BaseStyledForm, PasswordVerificationMixin,
                                SecurityMixin, LayoutMixin, ValidationMixin, forms.Form):
    """
     form for changing password while authenticated.
    """

    oldpassword = PasswordField(
        label=_("Current Password"),
        autocomplete="current-password",
        help_text=_("Enter your current password."),
    )

    password1 = SetPasswordField(
        label=_("New Password"),
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = PasswordField(
        label=_("Confirm New Password"),
        autocomplete="new-password",
        help_text=_("Enter your new password again to confirm."),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set user for password validation
        self.fields["password1"].user = self.user

        # Setup form layout
        self.setup_layout(
            fields=["oldpassword", "password1", "password2"],
            submit_text=_("Change Password"),
            show_links=True
        )

        # Apply styling to fields
        self.apply_field_styling(
            self.fields['oldpassword'],
            field_type='password',
            placeholder=_("Current password")
        )

        self.apply_field_styling(
            self.fields['password1'],
            field_type='password',
            placeholder=_("New password")
        )

        self.apply_field_styling(
            self.fields['password2'],
            field_type='password',
            placeholder=_("Confirm new password")
        )

    def clean_oldpassword(self):
        """Validate current password."""
        oldpassword = self.cleaned_data.get("oldpassword")
        if oldpassword and self.user and not self.user.check_password(oldpassword):
            adapter = get_adapter()
            if self.style_framework == 'tailwind':
                error_msg = _("The current password you entered is incorrect.")
            else:
                error_msg = adapter.validation_error("enter_current_password")
            raise forms.ValidationError(error_msg)
        return oldpassword

    def save(self):
        """Save the new password."""
        if self.user and self.cleaned_data.get("password1"):
            flows.password_change.change_password(
                self.user,
                self.cleaned_data["password1"]
            )
            return True
        return False

    def get_form_links(self):
        """Add cancel/back link."""
        links = super().get_form_links()
        style = self.get_styling('button', 'types')

        cancel_link = HTML(f'''
            <div class="text-center mt-3">
                <a href="{reverse("account_profile")}"
                   class="text-decoration-none {style.get('secondary', '')}">
                    {_("Cancel and return to profile")}
                </a>
            </div>
        ''')

        return links + [cancel_link]


# -------------------------------------------------------------------------
# SET PASSWORD FORM
# -------------------------------------------------------------------------

class SetPasswordForm(BaseStyledForm, PasswordVerificationMixin,
                             SecurityMixin, LayoutMixin, ValidationMixin, forms.Form):
    """
     form for setting a new password (without old password).
    """

    password1 = SetPasswordField(
        label=_("Password"),
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = PasswordField(
        label=_("Password (again)"),
        autocomplete="new-password",
        help_text=_("Enter your password again to confirm."),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set user for password validation
        self.fields["password1"].user = self.user

        # Setup form layout
        self.setup_layout(
            fields=["password1", "password2"],
            submit_text=_("Set Password"),
            show_links=False
        )

        # Apply styling to fields
        self.apply_field_styling(
            self.fields['password1'],
            field_type='password',
            placeholder=_("New password")
        )

        self.apply_field_styling(
            self.fields['password2'],
            field_type='password',
            placeholder=_("Confirm password")
        )

    def save(self):
        """Save the new password."""
        if self.user and self.cleaned_data.get("password1"):
            flows.password_change.change_password(
                self.user,
                self.cleaned_data["password1"]
            )
            return True
        return False


# -------------------------------------------------------------------------
# RESET PASSWORD FORM
# -------------------------------------------------------------------------

class ResetPasswordForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                               ValidationMixin, forms.Form):
    """
     form for requesting password reset.
    """

    email = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(
            attrs={
                "placeholder": _("Enter your email address"),
                "autocomplete": "email",
            }
        ),
        required=True,
        help_text=_("Enter the email address associated with your account."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["email"],
            submit_text=_("Send Reset Link"),
            show_links=True
        )

        # Apply styling
        self.apply_field_styling(
            self.fields['email'],
            field_type='email',
            placeholder=_("Email address")
        )

    def clean_email(self):
        """Validate email and check if user exists."""
        email = self.cleaned_data["email"].lower()
        adapter = get_adapter()
        email = adapter.clean_email(email)

        # Find users with this email
        self.users = filter_users_by_email(
            email,
            is_active=True,
            prefer_verified=True
        )

        # Prevent enumeration unless configured otherwise
        if not self.users and not app_settings.PREVENT_ENUMERATION:
            raise adapter.validation_error("unknown_email")

        return email

    def save(self, request, **kwargs):
        """Initiate password reset process."""
        email = self.cleaned_data["email"]

        if app_settings.PASSWORD_RESET_BY_CODE_ENABLED:
            # Use code-based password reset
            flows.password_reset_by_code.PasswordResetVerificationProcess.initiate(
                request=request,
                user=(self.users[0] if self.users else None),
                email=email,
            )
        else:
            # Use traditional token-based reset
            token_generator = kwargs.get("token_generator", default_token_generator)
            flows.password_reset.request_password_reset(
                request, email, self.users, token_generator
            )

        return email

    def get_form_links(self):
        """Add back to login link."""
        links = super().get_form_links()
        style = self.get_styling('button', 'types')

        back_link = HTML(f'''
            <div class="text-center mt-3">
                <a href="{reverse("account_login")}"
                   class="text-decoration-none {style.get('secondary', '')}">
                    {_("Back to login")}
                </a>
            </div>
        ''')

        return links + [back_link]


# -------------------------------------------------------------------------
# RESET PASSWORD KEY FORM
# -------------------------------------------------------------------------

class ResetPasswordKeyForm(BaseStyledForm, PasswordVerificationMixin,
                                  SecurityMixin, LayoutMixin, ValidationMixin, forms.Form):
    """
     form for resetting password with a key/token.
    """

    password1 = SetPasswordField(
        label=_("New Password"),
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = PasswordField(
        label=_("Confirm New Password"),
        autocomplete="new-password",
        help_text=_("Enter your new password again to confirm."),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super().__init__(*args, **kwargs)

        # Set user for password validation
        self.fields["password1"].user = self.user

        # Setup form layout
        self.setup_layout(
            fields=["password1", "password2"],
            submit_text=_("Change Password"),
            show_links=False
        )

        # Apply styling to fields
        self.apply_field_styling(
            self.fields['password1'],
            field_type='password',
            placeholder=_("New password")
        )

        self.apply_field_styling(
            self.fields['password2'],
            field_type='password',
            placeholder=_("Confirm new password")
        )

    def save(self):
        """Reset the user's password."""
        if self.user and self.cleaned_data.get("password1"):
            flows.password_reset.reset_password(
                self.user,
                self.cleaned_data["password1"]
            )
            return True
        return False
