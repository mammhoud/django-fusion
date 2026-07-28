"""Inventory forms — clean, no inline Bootstrap widget attrs (let CSS handle it)."""
from __future__ import annotations

from django import forms

from .models import Category, Delivery, Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description", "category", "quantity", "price", "expiring_date", "vendor"]
        widgets = {
            "expiring_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ["item", "customer_name", "phone_number", "location", "date", "is_delivered"]
        widgets = {
            "date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }
