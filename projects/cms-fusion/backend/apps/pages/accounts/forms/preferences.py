from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.domain.models.users.users import Person


class PreferencesSettingsForm(forms.Form):
    # Language & Region
    LANGUAGE_CHOICES = [
        ('en-us', _('English (US)')),
        ('en-gb', _('English (UK)')),
        ('es', _('Spanish')),
        ('fr', _('French')),
        ('de', _('German')),
    ]
    
    language = forms.ChoiceField(
        label=_("Language"),
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='en-us'
    )
    
    TIMEZONE_CHOICES = [
        ('America/New_York', _('(UTC-05:00) Eastern Time')),
        ('America/Los_Angeles', _('(UTC-08:00) Pacific Time')),
        ('UTC', _('(UTC+00:00) Greenwich Mean Time')),
        ('Europe/Paris', _('(UTC+01:00) Central European Time')),
    ]
    
    timezone = forms.ChoiceField(
        label=_("Time Zone"),
        choices=TIMEZONE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='America/New_York'
    )
    
    # Display Preferences
    dark_mode = forms.BooleanField(
        label=_("Dark mode"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    high_contrast = forms.BooleanField(
        label=_("High contrast mode"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    reduce_animations = forms.BooleanField(
        label=_("Reduce animations"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    # Content Density
    DENSITY_CHOICES = [
        ('compact', _('Compact')),
        ('comfortable', _('Comfortable')),
        ('spacious', _('Spacious')),
    ]
    
    density = forms.ChoiceField(
        label=_("Content Density"),
        choices=DENSITY_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'btn-check',
            'data-bs-toggle': 'buttons'
        }),
        initial='comfortable'
    )
    
    # Date & Time Format
    DATE_FORMAT_CHOICES = [
        ('MM/DD/YYYY', _('MM/DD/YYYY')),
        ('DD/MM/YYYY', _('DD/MM/YYYY')),
        ('YYYY-MM-DD', _('YYYY-MM-DD')),
    ]
    
    date_format = forms.ChoiceField(
        label=_("Date Format"),
        choices=DATE_FORMAT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='MM/DD/YYYY'
    )
    
    time_format = forms.ChoiceField(
        label=_("Time Format"),
        choices=[
            ('12h', _('12-hour clock')),
            ('24h', _('24-hour clock')),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='12h'
    )
