from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from crafts_ai.pipelines.models import Person


class PrivacySettingsForm(forms.Form):
    PROFILE_VISIBILITY_CHOICES = [
        ('public', _('Public - Anyone can see your profile')),
        ('members', _('Members Only - Only registered members can see your profile')),
        ('private', _('Private - Only you can see your profile')),
    ]
    
    profile_visibility = forms.ChoiceField(
        label=_("Profile Visibility"),
        choices=PROFILE_VISIBILITY_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    share_usage_data = forms.BooleanField(
        label=_("Share anonymized usage data to improve our services"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    allow_search_indexing = forms.BooleanField(
        label=_("Allow search engines to index your profile"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    show_online_status = forms.BooleanField(
        label=_("Show online status to other users"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    allow_contact = forms.BooleanField(
        label=_("Allow other members to contact you"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    show_email = forms.BooleanField(
        label=_("Show email address on profile"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
