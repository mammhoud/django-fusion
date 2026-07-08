"""
 phone verification forms with dual-framework styling.
Includes phone verification and phone change forms.
"""

from allauth.account.forms import BaseConfirmCodeForm
from allauth.account.internal.flows.phone_verification import phone_already_exists
from allauth.account.adapter import get_adapter
from crispy_forms.layout import HTML
from django import forms
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _

from django_fusion.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin


class VerifyPhoneForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                             ValidationMixin, BaseConfirmCodeForm):
    """
     phone verification form with dual-framework styling.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user", None)
        self.phone = kwargs.pop("phone", None)
        super().__init__(*args, **kwargs)

        # Update field labels and help text
        self.fields['code'].label = _("Phone Verification Code")
        self.fields['code'].help_text = _(
            "Enter the 6-digit verification code sent to your phone number."
        )

        # Setup form layout
        self.setup_layout(
            fields=["code"],
            submit_text=_("Verify Phone"),
            show_links=False
        )

        # Apply  styling
        self.apply_field_styling(
            self.fields['code'],
            field_type='text',
            placeholder=_("Enter 6-digit code"),
            icon='phone',
            icon_position='left'
        )

    def clean_code(self) -> str:
        """Validate verification code and check phone availability."""
        code = super().clean_code()
        if code:
            # Check if phone already exists for another user
            phone_already_exists(self.user, self.phone, always_raise=True)
        return code

    def get_submit_text(self):
        """Get submit button text."""
        return _("Verify Phone Number")


class ChangePhoneForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                             ValidationMixin, forms.Form):
    """
     form for changing phone number with dual-framework styling.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.current_phone = kwargs.pop("phone", None)
        super().__init__(*args, **kwargs)

        adapter = get_adapter()
        self.fields["phone"] = adapter.phone_form_field(required=True)

        # Customize the phone field
        self.fields["phone"].label = _("New Phone Number")
        self.fields["phone"].help_text = _(
            "Enter your new phone number including country code (e.g., +1 234 567 8900)."
        )

        # Setup form layout
        self.setup_layout(
            fields=["phone"],
            submit_text=_("Change Phone Number"),
            show_links=False
        )

        # Apply  styling
        self.apply_field_styling(
            self.fields['phone'],
            field_type='tel',
            placeholder=_("Enter new phone number"),
            icon='phone',
            icon_position='left'
        )

    def clean_phone(self):
        """Validate new phone number."""
        phone = self.cleaned_data["phone"]
        adapter = get_adapter()

        # Check if phone is same as current
        if phone == self.current_phone:
            raise adapter.validation_error("same_as_current")

        # Check if phone already exists for another user
        self.account_already_exists = phone_already_exists(self.user, phone)

        # Additional custom validation
        if not self._is_valid_phone_format(phone):
            raise forms.ValidationError(
                _("Please enter a valid phone number format (e.g., +1 234 567 8900).")
            )

        return phone

    def _is_valid_phone_format(self, phone):
        """Validate phone number format."""
        # Basic validation - can be extended with phone validation library
        import re

        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Check if it starts with + and has at least 10 digits after country code
        if cleaned.startswith('+'):
            digits = cleaned[1:]  # Remove +
            return len(digits) >= 10 and digits.isdigit()

        return False

    def get_form_links(self):
        """Add back link."""
        links = super().get_form_links()
        style = self.get_styling('button', 'types')

        back_link = HTML(f'''
            <div class="text-center mt-3">
                <a href="{reverse("account_profile")}"
                   class="text-decoration-none {style.get('secondary', '')}">
                    {_("Cancel and return to profile")}
                </a>
            </div>
        ''')

        return links + [back_link]


class PhoneVerificationRequestForm(BaseStyledForm, SecurityMixin, LayoutMixin,
                                         ValidationMixin, forms.Form):
    """
     form for requesting phone verification code.
    """

    phone = forms.CharField(
        label=_("Phone Number"),
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': _('+1 234 567 8900'),
            'inputmode': 'tel',
        }),
        help_text=_("Enter your phone number with country code to receive a verification code."),
    )

    verification_method = forms.ChoiceField(
        label=_("Verification Method"),
        choices=[
            ('sms', _("Send verification code via SMS")),
            ('call', _("Receive verification code via phone call")),
        ],
        initial='sms',
        widget=forms.RadioSelect(),
        help_text=_("Choose how you want to receive the verification code."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["phone", "verification_method"],
            submit_text=_("Send Verification Code"),
            show_links=False
        )

        # Apply styling
        self.apply_field_styling(
            self.fields['phone'],
            field_type='tel',
            placeholder=_("Phone number"),
            icon='phone',
            icon_position='left'
        )

        # Style radio buttons
        self.apply_field_styling(
            self.fields['verification_method'],
            field_type='radio'
        )

    def clean_phone(self):
        """Validate phone number."""
        phone = self.cleaned_data.get('phone')

        if phone:
            # Clean phone number
            import re
            cleaned = re.sub(r'[^\d+]', '', phone)

            # Basic validation
            if not cleaned.startswith('+'):
                raise forms.ValidationError(
                    _("Please include country code (e.g., +1 for US/Canada).")
                )

            if len(cleaned[1:]) < 10:
                raise forms.ValidationError(
                    _("Phone number appears to be too short. Please check and try again.")
                )

        return phone
