"""
Accounts models for the CRM site.

Adapted from original crm/accounts/models.py:
- StaffProfile replaces Profile (avoids conflict with django_fusion profile)
- Customer and Vendor inherit from django_fusion BaseModel
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from django_fusion.core.models.base import BaseModel

User = get_user_model()

STATUS_CHOICES = [
    ("INA", "Inactive"),
    ("A", "Active"),
    ("OL", "On leave"),
]

ROLE_CHOICES = [
    ("OP", "Operative"),
    ("EX", "Executive"),
    ("AD", "Admin"),
]


class StaffProfile(models.Model):
    """
    CRM staff profile — one-to-one extension of User.
    Replaces the original Profile model to avoid app_label conflicts.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="crm_profile",
        verbose_name=_("User"),
    )
    slug = AutoSlugField(unique=True, populate_from="user", verbose_name=_("Account ID"))
    telephone = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Telephone"))
    email = models.EmailField(max_length=150, blank=True, null=True, verbose_name=_("Email"))
    first_name = models.CharField(max_length=30, blank=True, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=30, blank=True, verbose_name=_("Last Name"))
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=12, default="INA", verbose_name=_("Status")
    )
    role = models.CharField(
        choices=ROLE_CHOICES, max_length=12, blank=True, null=True, verbose_name=_("Role")
    )

    class Meta:
        app_label = "crm_accounts"
        ordering = ["slug"]
        verbose_name = _("Staff Profile")
        verbose_name_plural = _("Staff Profiles")

    def __str__(self) -> str:
        return f"{self.user.username} – {self.get_role_display() or 'no role'}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.user.username


class Vendor(BaseModel):
    """Supplier / vendor."""

    name = models.CharField(max_length=80, verbose_name=_("Name"))
    slug = AutoSlugField(unique=True, populate_from="name")
    phone_number = models.CharField(max_length=30, blank=True, null=True, verbose_name=_("Phone"))
    address = models.CharField(max_length=120, blank=True, null=True, verbose_name=_("Address"))

    class Meta:
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Customer(BaseModel):
    """CRM customer."""

    first_name = models.CharField(max_length=256, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Last Name"))
    address = models.TextField(max_length=256, blank=True, null=True, verbose_name=_("Address"))
    email = models.EmailField(max_length=256, blank=True, null=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name=_("Phone"))
    loyalty_points = models.IntegerField(default=0, verbose_name=_("Loyalty Points"))

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return self.get_full_name()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name or ''}".strip()

    def to_select2(self) -> dict:
        return {"label": self.get_full_name(), "value": str(self.id)}
