"""
Cloud Master CRM models for Full POS Portal.
Replaces the old Sanic sidecar cloud CRM with Django models.

@tested pos-portal/full - Cloud CRM models
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """CRM Company entity."""

    name = models.CharField(_("name"), max_length=200)
    website = models.URLField(_("website"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    address = models.TextField(_("address"), blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    industry = models.CharField(_("industry"), max_length=100, blank=True)
    description = models.TextField(_("description"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Contact(models.Model):
    """CRM Contact entity - linked to Company and optionally to POS Customer."""

    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contacts", verbose_name=_("company"),
    )
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    mobile = models.CharField(_("mobile"), max_length=50, blank=True)
    job_title = models.CharField(_("job title"), max_length=200, blank=True)
    source = models.CharField(_("source"), max_length=100, blank=True)
    notes = models.TextField(_("notes"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    # Link to POS Customer
    pos_customer_id = models.IntegerField(
        _("POS customer ID"), blank=True, null=True, editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Deal(models.Model):
    """CRM Deal entity - tracks sales pipeline progress."""

    PIPELINE_CHOICES = [
        ("new", "New Lead"),
        ("qualified", "Qualified"),
        ("proposal", "Proposal"),
        ("negotiation", "Negotiation"),
        ("won", "Closed Won"),
        ("lost", "Closed Lost"),
    ]

    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deals", verbose_name=_("contact"),
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deals", verbose_name=_("company"),
    )
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    value = models.DecimalField(_("value"), max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(_("currency"), max_length=3, default="USD")
    stage = models.CharField(_("stage"), max_length=20, choices=PIPELINE_CHOICES, default="new")
    probability = models.IntegerField(_("probability (%)"), default=10)
    expected_close_date = models.DateField(_("expected close date"), blank=True, null=True)
    is_closed = models.BooleanField(_("closed"), default=False)
    is_won = models.BooleanField(_("won"), default=False)
    lost_reason = models.TextField(_("lost reason"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("deal")
        verbose_name_plural = _("deals")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.stage})"
