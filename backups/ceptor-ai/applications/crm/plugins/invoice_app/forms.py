from __future__ import annotations

from django import forms
from .models import Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["customer_name", "contact_number", "item", "price_per_item", "quantity", "shipping"]
