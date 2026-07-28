"""Bill model — adapted to use BaseModel."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from django_fusion.core.models.base import BaseModel


class Bill(BaseModel):
    """An expense bill payable to an institution."""

    slug = AutoSlugField(unique=True, populate_from="date")
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))
    institution_name = models.CharField(max_length=80, verbose_name=_("Institution"))
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    payment_details = models.CharField(max_length=255, verbose_name=_("Payment Details"))
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Amount Owing")
    )
    status = models.BooleanField(default=False, verbose_name=_("Paid"))

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")

    def __str__(self) -> str:
        return f"{self.institution_name} — {'Paid' if self.status else 'Unpaid'}"
