"""
 signup forms with dual-framework styling.
Includes additional fields, terms agreement, and  validation.
"""

from allauth import app_settings
from allauth.account.forms import SignupForm
from crispy_forms.layout import HTML, Layout
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_fusion.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin


class SignupForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                        ValidationMixin, SignupForm):
    """
     signup form with additional fields and dual-framework styling.
    """

    first_name = forms.CharField(
        max_length=30,
        label=_("First name"),
        required=True,
        help_text=_("Enter your first name"),
    )

    last_name = forms.CharField(
        max_length=30,
        label=_("Last name"),
        required=True,
        help_text=_("Enter your last name"),
    )

    phone = forms.CharField(
        max_length=20,
        label=_("Phone number"),
        required=False,
        help_text=_("Optional phone number for account recovery"),
    )

    terms = forms.BooleanField(
        label=_("Terms and conditions"),
        required=True,
        error_messages={
            "required": _("You must agree to the Terms and Conditions to sign up.")
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["first_name", "last_name", "email", "phone",
                   "username", "password1", "password2", "terms"],
            submit_text=_("Create Account"),
            show_links=True
        )

        # Apply initial styling
        self.apply_initial_styling()

        # Update labels and placeholders
        self.update_field_configurations()

    def apply_initial_styling(self):
        """Apply initial styling to all form fields."""
        field_configs = [
            ('first_name', 'text', _("First name")),
            ('last_name', 'text', _("Last name")),
            ('email', 'email', _("Email address")),
            ('phone', 'tel', _("Phone number")),
            ('username', 'text', _("Username")),
            ('password1', 'password', _("Password")),
            ('password2', 'password', _("Confirm password")),
        ]

        for field_name, field_type, placeholder in field_configs:
            if field_name in self.fields:
                self.apply_field_styling(
                    self.fields[field_name],
                    field_type=field_type,
                    placeholder=placeholder
                )

        # Special styling for terms checkbox
        if 'terms' in self.fields:
            self.apply_field_styling(
                self.fields['terms'],
                field_type='checkbox'
            )

    def update_field_configurations(self):
        """Update field configurations for better UX."""
        # Make username field optional if not required
        if not app_settings.USERNAME_REQUIRED:
            self.fields['username'].required = False
            self.fields['username'].help_text = _("Optional")

        # Add help text for password
        self.fields['password1'].help_text = _(
            "Use at least 8 characters with a mix of letters, numbers, and symbols."
        )

    def setup_layout(self, fields, submit_text=None, show_links=True):
        """Override to include terms agreement in layout."""
        super().setup_layout(fields, submit_text, show_links)

        # Customize layout for terms agreement
        if 'terms' in self.fields:
            # Remove terms from regular layout and add custom HTML
            terms_field = self.fields.pop('terms')

            # Create custom terms layout
            checkbox_class = self.get_styling('input', 'types').get('checkbox', '')
            style = self.get_styling('button', 'types')

            terms_html = HTML(f'''
                <div class="form-check mb-3">
                    <input type="checkbox" name="terms" id="id_terms"
                           class="{checkbox_class}" required>
                    <label for="id_terms" class="form-check-label">
                        {_("I agree to the")}
                        <a href="{reverse("terms")}"
                           class="text-decoration-none {style.get('primary', '')}">
                            {_("Terms and Conditions")}
                        </a>
                    </label>
                </div>
            ''')

            # Insert terms before submit button
            layout_fields = list(self.helper.layout.fields)
            submit_index = len(layout_fields) - 1
            layout_fields.insert(submit_index, terms_html)
            self.helper.layout = Layout(*layout_fields)

            # Put field back
            self.fields['terms'] = terms_field

    def clean_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Basic phone validation - extend as needed
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError(
                    _("Please enter a valid phone number with at least 10 digits.")
                )
        return phone

    def clean(self):
        """Additional form-wide validation."""
        cleaned_data = super().clean()

        # Check if passwords match
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', _("Passwords do not match."))

        return cleaned_data

    def save(self, request):
        """Save user with additional information."""
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if self.cleaned_data.get('phone'):
            user.phone = self.cleaned_data['phone']

        user.save()
        return user

    def get_form_links(self):
        """Override to add login link."""
        links = super().get_form_links()
        style = self.get_styling('button', 'types')

        login_link = HTML(f'''
            <div class="text-center mt-2">
                <span class="text-muted">{_("Already have an account?")}</span>
                <a href="{reverse("account_login")}"
                   class="text-decoration-none ms-1 {style.get('primary', '')}">
                    {_("Sign in")}
                </a>
            </div>
        ''')

        return links + [login_link]
