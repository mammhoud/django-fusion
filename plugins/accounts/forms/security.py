from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_rseal.pipelines.models import Person


class SecuritySettingsForm(forms.Form):
    # Two-Factor Authentication
    two_factor_enabled = forms.BooleanField(
        label=_("Enable Two-Factor Authentication"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        }),
        help_text=_("Add an extra layer of security to your account")
    )
    
    # Login Notifications
    login_notifications = forms.BooleanField(
        label=_("Send email notification for new logins"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    # Session Management
    SESSION_TIMEOUT_CHOICES = [
        (15, _('15 minutes')),
        (30, _('30 minutes')),
        (60, _('1 hour')),
        (1440, _('24 hours')),
        (10080, _('1 week')),
    ]
    
    session_timeout = forms.ChoiceField(
        label=_("Session Timeout"),
        choices=SESSION_TIMEOUT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial=1440
    )
    
    # Password Requirements
    password_strength_requirement = forms.ChoiceField(
        label=_("Password Strength Requirement"),
        choices=[
            ('low', _('Low - Minimum 6 characters')),
            ('medium', _('Medium - Minimum 8 characters with letters and numbers')),
            ('high', _('High - Minimum 12 characters with mixed case, numbers, and symbols')),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='medium'
    )

