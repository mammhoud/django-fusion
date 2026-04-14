from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_rseal.pipelines.models import Person


class BillingSettingsForm(forms.Form):
    # Subscription Plan
    PLAN_CHOICES = [
        ('free', _('Free Plan')),
        ('pro', _('Pro Plan - $29.99/month')),
        ('business', _('Business Plan - $99.99/month')),
        ('enterprise', _('Enterprise Plan - Custom pricing')),
    ]
    
    plan = forms.ChoiceField(
        label=_("Subscription Plan"),
        choices=PLAN_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Billing Cycle
    BILLING_CYCLE_CHOICES = [
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly - Save 20%')),
    ]
    
    billing_cycle = forms.ChoiceField(
        label=_("Billing Cycle"),
        choices=BILLING_CYCLE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='monthly'
    )
    
    # Payment Method
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', _('Credit Card')),
        ('paypal', _('PayPal')),
        ('bank_transfer', _('Bank Transfer')),
    ]
    
    payment_method = forms.ChoiceField(
        label=_("Payment Method"),
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='credit_card'
    )
    
    # Auto Renew
    auto_renew = forms.BooleanField(
        label=_("Auto-renew subscription"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        }),
        help_text=_("Automatically renew your subscription at the end of each billing period")
    )
    
    # Billing Address
    billing_name = forms.CharField(
        label=_("Billing Name"),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Name on card')
        })
    )
    
    billing_address = forms.CharField(
        label=_("Billing Address"),
        max_length=300,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Street address, City, State, ZIP')
        })
    )
    
    # Tax Information
    tax_id = forms.CharField(
        label=_("Tax ID/VAT Number"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter tax ID if applicable')
        })
    )
    
    # Invoice Preferences
    send_invoices = forms.BooleanField(
        label=_("Email me invoices"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    paperless_billing = forms.BooleanField(
        label=_("Paperless billing"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )