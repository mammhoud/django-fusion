"""Loop-CRM SaaS billing — subscription state for the workspace itself.

Separate from ``apps.finance`` (the product's B2B revenue ledger): these models
gate the workspace's plan, seat count, and Stripe subscription. ``Plan`` is the
enforceable source of truth for limits; the Wagtail pricing page stays editorial
(marketing copy) and is rendered alongside ``/apis/billing/plans/``.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import Workspace


class Plan(models.Model):
    """A purchasable subscription tier (source of truth for feature/seat limits)."""

    PERIOD_CHOICES = [
        ("monthly", _("Monthly")),
        ("annual", _("Annual")),
    ]

    slug = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=120, verbose_name=_("name"))
    price_cents = models.PositiveIntegerField(default=0, verbose_name=_("price (cents)"))
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default="monthly", verbose_name=_("period"))
    seat_limit = models.PositiveIntegerField(default=1, verbose_name=_("seat limit"))
    # Feature flags are declarative keys consumed by ``apps.billing.gates``.
    feature_flags = models.JSONField(default=dict, blank=True, verbose_name=_("feature flags"))
    stripe_price_id = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Stripe price id"))
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    class Meta:
        ordering = ["price_cents", "name"]
        verbose_name = _("plan")
        verbose_name_plural = _("plans")

    def __str__(self) -> str:
        return f"{self.name} ({self.get_period_display()})"

    @property
    def monthly_price_dollars(self) -> str:
        return f"{self.price_cents / 100:.2f}"


class BillingAccount(models.Model):
    """1:1 with a Workspace — plan + Stripe subscription state."""

    STATUS_CHOICES = [
        ("trial", _("Trial")),
        ("active", _("Active")),
        ("past_due", _("Past due")),
        ("canceled", _("Canceled")),
    ]

    workspace = models.OneToOneField(
        Workspace, on_delete=models.CASCADE, related_name="billing_account"
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name="accounts")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trial")
    stripe_customer_id = models.CharField(max_length=255, blank=True, default="")
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default="")
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workspace"]
        verbose_name = _("billing account")
        verbose_name_plural = _("billing accounts")

    def __str__(self) -> str:
        return f"{self.workspace.name} · {self.get_status_display()}"

    @property
    def is_entitled(self) -> bool:
        """True while the workspace may use gated features."""
        if self.status in {"active", "trial"}:
            return True
        if self.trial_ends_at and self.trial_ends_at > timezone.now():
            return True
        return False


class Seat(models.Model):
    """An occupied seat in a workspace (one row per member on a seat-limited plan)."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="seats")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="billing_seats")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["workspace", "user"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "user"], name="uniq_seat_workspace_user"),
        ]
        verbose_name = _("seat")
        verbose_name_plural = _("seats")

    def __str__(self) -> str:
        return f"{self.workspace.name} · {self.user}"
