"""
Newsletter Subscription Form
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from django_rseal.content.forms import BaseModelForm
from django_rseal.content.models.newsletter import Subscriber


class SubscriptionForm(BaseModelForm):
    """
    Form for newsletter subscription with HTMX support.
    """

    class Meta:
        model = Subscriber
        fields = ["email", "name"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "placeholder": _("Enter your email"),
                "required": True,
            }),
            "name": forms.TextInput(attrs={
                "placeholder": _("Your name (optional)"),
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower().strip()

        # Check if already subscribed
        existing = Subscriber.objects.filter(email=email).first()
        if existing:
            if existing.status == "confirmed":
                raise forms.ValidationError(_("This email is already subscribed."))
            elif existing.status == "pending":
                raise forms.ValidationError(
                    _("This email is pending confirmation. Please check your inbox.")
                )
            elif existing.status == "unsubscribed":
                # Allow re-subscription
                pass

        return email

    def save(self, commit=True, source=""):
        instance = super().save(commit=False)
        instance.source = source

        # Check for existing unsubscribed user
        existing = Subscriber.objects.filter(email=instance.email).first()
        if existing and existing.status == "unsubscribed":
            # Reactivate existing subscriber
            existing.status = "pending"
            existing.unsubscribed_at = None
            existing.regenerate_tokens()
            if commit:
                existing.save()
            return existing

        if commit:
            instance.save()
        return instance
