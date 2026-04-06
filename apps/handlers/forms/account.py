from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_grep.pipelines.models import Person


class AccountSettingsForm(forms.Form):
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your first name')
        })
    )
    
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your last name')
        })
    )
    
    email = forms.EmailField(
        label=_("Email Address"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email address')
        })
    )
    
    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your username'),
            'readonly': True,
            'disabled': True
        })
    )
    
    phone = forms.CharField(
        label=_("Phone Number"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('+1 (555) 123-4567')
        })
    )
    
    location = forms.CharField(
        label=_("Location"),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('City, Country')
        })
    )
    
    bio = forms.CharField(
        label=_("Bio"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Tell us about yourself...')
        })
    )
    
    public_profile = forms.BooleanField(
        label=_("Make profile public"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already in use by another user
        from django.contrib.auth.models import User
        user = self.initial.get('user_id')
        if User.objects.filter(email=email).exclude(id=user).exists():
            raise ValidationError(_("This email is already in use."))
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and not phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
            raise ValidationError(_("Enter a valid phone number."))
        return phone
