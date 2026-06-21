"""
Contact and corporate models for django_rseal.
Provides Contact, ContactEmail, ContactPhone, and Corporate models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Contact(models.Model):
    """A contact person or entity."""

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_("Phone"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "django_rseal"
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __str__(self) -> str:
        return self.name


class ContactEmail(models.Model):
    """Additional email addresses for a contact."""

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="emails"
    )
    email = models.EmailField(verbose_name=_("Email"))
    label = models.CharField(max_length=50, blank=True, default="work")

    class Meta:
        app_label = "django_rseal"
        verbose_name = _("Contact Email")
        verbose_name_plural = _("Contact Emails")

    def __str__(self) -> str:
        return f"{self.contact} — {self.email}"


class ContactPhone(models.Model):
    """Additional phone numbers for a contact."""

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="phones"
    )
    phone_number = models.CharField(max_length=50, verbose_name=_("Phone Number"))
    label = models.CharField(max_length=50, blank=True, default="work")

    class Meta:
        app_label = "django_rseal"
        verbose_name = _("Contact Phone")
        verbose_name_plural = _("Contact Phones")

    def __str__(self) -> str:
        return f"{self.contact} — {self.phone_number}"


class Corporate(models.Model):
    """A corporate entity / company."""

    name = models.CharField(max_length=255, verbose_name=_("Company Name"))
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    contacts = models.ManyToManyField(
        Contact, blank=True, related_name="companies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "django_rseal"
        verbose_name = _("Corporate")
        verbose_name_plural = _("Corporates")

    def __str__(self) -> str:
        return self.name


# Alias used in some imports
Company = Corporate

__all__ = ["Contact", "ContactEmail", "ContactPhone", "Corporate", "Company"]
