"""Transaction forms."""
from __future__ import annotations

from django import forms
from .models import Purchase


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["item", "price", "description", "vendor", "quantity", "delivery_date", "delivery_status"]
        widgets = {
            "delivery_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 2}),
        }
