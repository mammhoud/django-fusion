"""
Enhanced admin forms with dual-framework styling.
Includes user admin forms and Wagtail group forms.
"""

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

User = get_user_model()

from django_osoul.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin


class EnhancedUserAdminCreationForm(
    BaseStyledForm, SecurityMixin, LayoutMixin, ValidationMixin, admin_forms.UserCreationForm
):
    """
    Enhanced user creation form for admin with dual-framework styling.
    """

    email = EmailField(
        label=_("Email Address"),
        required=True,
        error_messages={
            "unique": _("This email address is already in use."),
            "invalid": _("Please enter a valid email address."),
        },
        help_text=_("Required. Must be a valid email address."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["email", "password1", "password2"],
            submit_text=_("Create User"),
            show_links=False,
        )

        # Apply styling to fields
        self.apply_field_styling(
            self.fields["email"], field_type="email", placeholder=_("Enter email address")
        )

        self.apply_field_styling(
            self.fields["password1"], field_type="password", placeholder=_("Password")
        )

        self.apply_field_styling(
            self.fields["password2"], field_type="password", placeholder=_("Confirm password")
        )

        # Make email field required
        self.fields["email"].required = True

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class EnhancedUserAdminChangeForm(
    BaseStyledForm, SecurityMixin, LayoutMixin, ValidationMixin, admin_forms.UserChangeForm
):
    """
    Enhanced user change form for admin with dual-framework styling.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get field list excluding password
        fields = [
            field
            for field in self.fields.keys()
            if field not in ["password", "last_login", "date_joined"]
        ]

        # Setup form layout
        self.setup_layout(fields=fields, submit_text=_("Update User"), show_links=False)

        # Apply styling to all fields
        for field_name, field in self.fields.items():
            if field_name in ["password", "last_login", "date_joined"]:
                continue

            field_type = self.detect_field_type(field)
            self.apply_field_styling(field, field_type=field_type, placeholder=field.label)

    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class EnhancedAdminSignupForm(
    BaseStyledForm, SecurityMixin, LayoutMixin, ValidationMixin, SignupForm
):
    """
    Enhanced signup form for admin interface.
    """

    first_name = forms.CharField(
        max_length=30,
        label=_("First Name"),
        required=True,
        help_text=_("Enter user's first name"),
    )

    last_name = forms.CharField(
        max_length=30,
        label=_("Last Name"),
        required=True,
        help_text=_("Enter user's last name"),
    )

    phone = forms.CharField(
        max_length=20,
        label=_("Phone Number"),
        required=False,
        help_text=_("Optional phone number"),
    )

    is_active = forms.BooleanField(
        label=_("Active"),
        required=False,
        initial=True,
        help_text=_("Designates whether this user should be treated as active."),
    )

    is_staff = forms.BooleanField(
        label=_("Staff Status"),
        required=False,
        initial=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_superuser = forms.BooleanField(
        label=_("Superuser Status"),
        required=False,
        initial=False,
        help_text=_(
            "Designates that this user has all permissions without explicitly assigning them."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=[
                "first_name",
                "last_name",
                "email",
                "phone",
                "username",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ],
            submit_text=_("Create User Account"),
            show_links=False,
        )

        # Apply styling
        field_configs = [
            ("first_name", "text", _("First name")),
            ("last_name", "text", _("Last name")),
            ("email", "email", _("Email address")),
            ("phone", "tel", _("Phone number")),
            ("username", "text", _("Username")),
            ("password1", "password", _("Password")),
            ("password2", "password", _("Confirm password")),
        ]

        for field_name, field_type, placeholder in field_configs:
            if field_name in self.fields:
                self.apply_field_styling(
                    self.fields[field_name], field_type=field_type, placeholder=placeholder
                )

        # Style boolean fields
        for field_name in ["is_active", "is_staff", "is_superuser"]:
            if field_name in self.fields:
                self.apply_field_styling(self.fields[field_name], field_type="checkbox")

    def save(self, request):
        """Save user with admin fields."""
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone = self.cleaned_data.get("phone", "")
        user.is_active = self.cleaned_data.get("is_active", True)
        user.is_staff = self.cleaned_data.get("is_staff", False)
        user.is_superuser = self.cleaned_data.get("is_superuser", False)
        user.save()
        return user


class EnhancedSocialSignupForm(
    BaseStyledForm, SecurityMixin, LayoutMixin, ValidationMixin, SocialSignupForm
):
    """
    Enhanced social signup form for admin interface.
    """

    first_name = forms.CharField(
        max_length=30,
        label=_("First Name"),
        required=False,
        help_text=_("Enter your first name"),
    )

    last_name = forms.CharField(
        max_length=30,
        label=_("Last Name"),
        required=False,
        help_text=_("Enter your last name"),
    )

    phone = forms.CharField(
        max_length=20,
        label=_("Phone Number"),
        required=False,
        help_text=_("Optional phone number"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get social account data if available
        if hasattr(self, "sociallogin"):
            if self.sociallogin.account.extra_data.get("given_name"):
                self.fields["first_name"].initial = self.sociallogin.account.extra_data[
                    "given_name"
                ]
            if self.sociallogin.account.extra_data.get("family_name"):
                self.fields["last_name"].initial = self.sociallogin.account.extra_data[
                    "family_name"
                ]

        # Setup form layout
        self.setup_layout(
            fields=["first_name", "last_name", "email", "phone", "username"],
            submit_text=_("Complete Signup"),
            show_links=False,
        )

        # Apply styling
        field_configs = [
            ("first_name", "text", _("First name")),
            ("last_name", "text", _("Last name")),
            ("email", "email", _("Email address")),
            ("phone", "tel", _("Phone number")),
            ("username", "text", _("Username")),
        ]

        for field_name, field_type, placeholder in field_configs:
            if field_name in self.fields:
                self.apply_field_styling(
                    self.fields[field_name], field_type=field_type, placeholder=placeholder
                )

    def save(self, request):
        """Save user from social signup."""
        user = super().save(request)

        # Save additional fields if provided
        if self.cleaned_data.get("first_name"):
            user.first_name = self.cleaned_data["first_name"]
        if self.cleaned_data.get("last_name"):
            user.last_name = self.cleaned_data["last_name"]
        if self.cleaned_data.get("phone"):
            user.phone = self.cleaned_data["phone"]

        user.save()
        return user
