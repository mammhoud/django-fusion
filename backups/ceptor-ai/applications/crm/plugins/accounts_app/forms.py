"""Accounts forms for the CRM site."""
from __future__ import annotations

from django import forms

from .models import Customer, StaffProfile, Vendor


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ["first_name", "last_name", "telephone", "email", "role", "status"]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "address", "email", "phone", "loyalty_points"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["name", "phone_number", "address"]
