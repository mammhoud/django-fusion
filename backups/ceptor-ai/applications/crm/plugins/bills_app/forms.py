from __future__ import annotations

from django import forms
from .models import Bill


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = [
            "institution_name", "phone_number", "email", "address",
            "description", "payment_details", "amount", "status",
        ]
