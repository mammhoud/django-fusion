from __future__ import annotations

"""
POS Full — Loyalty & Client Settings managed models.

ClientCategory      — tier/category for clients (people) based on loyalty points.
LoyaltyTransaction  — points ledger (earn / redeem / adjust / expire) per customer.
UserSettings        — per-user POS settings mirroring the front Settings page
                      (restaurant_name, currency, tax_rate, ...) plus
                      user-specific preferences (theme, language, notifications,
                      inactivity timeout).

Tables: full_client_categories, full_loyalty_transactions, full_user_settings
Each model includes DataToken-sync fields (is_synced, synced_at, sync_status)
following the same pattern as models/pos.py.
"""

from django.conf import settings as django_settings
from django.db import models


# ===========================================================================
# ClientCategory — loyalty tier for people / clients
# ===========================================================================

class ClientCategory(models.Model):
    """Tier/category that groups clients by loyalty points and spending.

    The tier drives reward multipliers, automatic discounts, and perk lists.
    A customer is placed in the highest tier whose ``min_points`` threshold
    their loyalty balance meets.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    min_points = models.IntegerField(
        default=0,
        help_text="Minimum loyalty points required to reach this tier",
    )
    points_per_currency = models.IntegerField(
        default=1,
        help_text="Loyalty points earned per 1 unit of currency spent (e.g. 1 pt per $1)",
    )
    points_to_currency = models.IntegerField(
        default=100,
        help_text="Points required to redeem 1 unit of currency as a reward",
    )
    discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Automatic percentage discount for this tier (0–100)",
    )
    perks = models.JSONField(
        default=list, blank=True,
        help_text='List of perk descriptions, e.g. ["Free dessert", "Priority seating"]',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_client_categories"
        ordering = ["min_points", "name"]
        verbose_name_plural = "client categories"

    def __str__(self) -> str:
        return f"{self.name} ({self.min_points}+ pts)"

    @property
    def customer_count(self) -> int:
        """Number of customers currently in this tier."""
        try:
            return self.customers.filter(is_active=True).count()
        except Exception:
            return 0


# ===========================================================================
# LoyaltyTransaction — points ledger entries
# ===========================================================================

class LoyaltyTransaction(models.Model):
    """One ledger entry changing a customer's loyalty balance."""

    TRANSACTION_TYPES = [
        ("earn", "Earn"),
        ("redeem", "Redeem"),
        ("adjust", "Adjustment"),
        ("expire", "Expiry"),
        ("reversal", "Reversal"),
    ]

    customer = models.ForeignKey(
        "Customer", on_delete=models.CASCADE, related_name="loyalty_transactions",
    )
    sale = models.ForeignKey(
        "Sale", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="loyalty_transactions",
        help_text="Sale that earned/redeemed these points (if any)",
    )
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, default="earn",
    )
    points_change = models.IntegerField(
        help_text="Positive = points earned, negative = points redeemed/expired",
    )
    balance_after = models.IntegerField(
        default=0, help_text="Customer's loyalty balance after this entry",
    )
    reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_loyalty_transactions"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        sign = "+" if self.points_change >= 0 else ""
        return f"{self.get_transaction_type_display()} {sign}{self.points_change} pts — {self.customer}"


# ===========================================================================
# UserSettings — per-user POS settings (mirrors front Settings + preferences)
# ===========================================================================

class UserSettings(models.Model):
    """Per-user POS settings.

    Mirrors the fields of the frontend Settings page (restaurant_name,
    currency, tax_rate, dine_in_tables, delivery fees, ...) so the admin can
    manage the same data as the POS front settings page, plus user-specific
    preferences (theme, language, notifications, inactivity timeout).
    """

    THEME_CHOICES = [("dark", "Dark"), ("light", "Light"), ("system", "System")]
    LANGUAGE_CHOICES = [("en", "English"), ("ar", "Arabic"), ("fr", "French")]

    user = models.OneToOneField(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pos_settings",
        help_text="Django user (superuser) this settings row belongs to",
    )

    # ── Business settings (same data shape as the front Settings page) ──
    restaurant_name = models.CharField(max_length=200, default="POS")
    address = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default="USD")
    opening_time = models.CharField(max_length=5, blank=True, default="09:00")
    closing_time = models.CharField(max_length=5, blank=True, default="22:00")
    receipt_footer = models.TextField(blank=True, default="")
    logo = models.TextField(blank=True, default="", help_text="Base64 data-URL logo")
    dine_in_tables = models.IntegerField(default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ── User preferences ──
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default="dark")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")
    notifications_enabled = models.BooleanField(default=True)
    inactivity_timeout = models.CharField(max_length=20, default="30",
        help_text="Minutes before auto-lock; 'never' disables")
    two_factor_enabled = models.BooleanField(default=False)

    # ── Fusion render-mode preference (operator-facing) ──────────────────
    # Mirrors the /fusion/session-mode/ toggle: which content-delivery mode
    # this operator prefers. 'default' follows FUSION_RENDER_FIRST_DEFAULT;
    # 'fusion' forces server-rendered HTML first; 'data' forces JSON APIs.
    # A ``FormintSessionModeMiddleware`` seeds each authenticated user's
    # session from this field (see formint/middleware.py).
    FUSION_RENDER_MODE_CHOICES = [
        ("default", "Default (settings)"),
        ("fusion", "Fusion render-first"),
        ("data", "Data APIs"),
    ]
    fusion_render_mode = models.CharField(
        max_length=10,
        choices=FUSION_RENDER_MODE_CHOICES,
        default="default",
        help_text=(
            "Content-delivery mode: 'Fusion render-first' serves finished server "
            "HTML, 'Data APIs' serves JSON for the client, 'Default (settings)' "
            "follows FUSION_RENDER_FIRST_DEFAULT."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_user_settings"
        verbose_name_plural = "user settings"

    def __str__(self) -> str:
        return f"Settings — {self.user}"

    @property
    def user_email(self) -> str:
        return getattr(self.user, "email", "") or getattr(self.user, "username", "")
