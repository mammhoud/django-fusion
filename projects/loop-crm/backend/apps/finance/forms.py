"""Forms for the finance render-first and HTMX surfaces."""
from __future__ import annotations

from decimal import Decimal

from django import forms

from apps.crm.models import Company, Contact, Deal

from .models import Invoice, Payment


def _profile_workspace_id(request):
    try:
        return request.user.profile.workspace_id
    except Exception:  # noqa: BLE001 - legacy accounts may not have a profile
        return None


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "workspace",
            "number",
            "company",
            "contact",
            "deal",
            "currency",
            "status",
            "issued_on",
            "due_on",
            "subtotal",
            "tax",
            "notes",
        ]
        widgets = {
            "number": forms.TextInput(attrs={"placeholder": "INV-2026-0042"}),
            "issued_on": forms.DateInput(attrs={"type": "date"}),
            "due_on": forms.DateInput(attrs={"type": "date"}),
            "subtotal": forms.NumberInput(attrs={"step": "0.01", "placeholder": "92500.00"}),
            "tax": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Payment terms and context."}),
        }

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        workspace_id = _profile_workspace_id(request) if request else None
        if workspace_id is not None:
            self.fields["workspace"].queryset = self.fields["workspace"].queryset.filter(pk=workspace_id)
            for field_name, queryset in (
                ("company", Company.objects.filter(workspace_id=workspace_id).order_by("name")),
                ("contact", Contact.objects.filter(workspace_id=workspace_id).order_by("last_name", "first_name")),
                ("deal", Deal.objects.filter(workspace_id=workspace_id).order_by("-created_at")),
            ):
                self.fields[field_name].queryset = queryset
        else:
            self.fields["company"].queryset = Company.objects.order_by("name")
            self.fields["contact"].queryset = Contact.objects.order_by("last_name", "first_name")
            self.fields["deal"].queryset = Deal.objects.order_by("-created_at")

    def clean(self):
        cleaned = super().clean()
        workspace = cleaned.get("workspace")
        workspace_id = workspace.pk if workspace else None
        if workspace_id:
            for name in ("company", "contact", "deal"):
                related = cleaned.get(name)
                if related and related.workspace_id != workspace_id:
                    self.add_error(name, "This record must belong to the selected workspace.")
        company = cleaned.get("company")
        contact = cleaned.get("contact")
        deal = cleaned.get("deal")
        if company and contact and contact.company_id != company.pk:
            self.add_error("contact", "The contact must belong to the selected company.")
        if company and deal and deal.company_id != company.pk:
            self.add_error("deal", "The deal must belong to the selected company.")
        return cleaned

    def save(self, commit=True):
        invoice = super().save(commit=False)
        user = getattr(self.request, "user", None)
        if getattr(user, "is_authenticated", False):
            invoice.created_by = user
        if commit:
            invoice.save()
        return invoice


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["workspace", "invoice", "amount", "paid_on", "method", "reference"]
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "placeholder": "2500.00"}),
            "paid_on": forms.DateInput(attrs={"type": "date"}),
            "reference": forms.TextInput(attrs={"placeholder": "BANK-REF-1042"}),
        }

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        workspace_id = _profile_workspace_id(request) if request else None
        queryset = Invoice.objects.select_related("company").order_by("-issued_on")
        if workspace_id is not None:
            self.fields["workspace"].queryset = self.fields["workspace"].queryset.filter(pk=workspace_id)
            queryset = queryset.filter(workspace_id=workspace_id)
        self.fields["invoice"].queryset = queryset

    def clean(self):
        cleaned = super().clean()
        workspace = cleaned.get("workspace")
        invoice = cleaned.get("invoice")
        amount = cleaned.get("amount")
        if workspace and invoice and invoice.workspace_id != workspace.pk:
            self.add_error("invoice", "The invoice must belong to the selected workspace.")
        if invoice and amount is not None and amount > invoice.outstanding:
            self.add_error("amount", f"Payment cannot exceed the outstanding balance of {invoice.outstanding}.")
        return cleaned

    def save(self, commit=True):
        payment = super().save(commit=False)
        user = getattr(self.request, "user", None)
        if getattr(user, "is_authenticated", False):
            payment.created_by = user
        if commit:
            payment.save()
            invoice = payment.invoice
            invoice.status = "paid" if invoice.outstanding <= Decimal("0.00") else "partially_paid"
            invoice.save(update_fields=["status", "updated_at"])
        return payment
