"""
POS Full — Gift Card models (P2, Professional+).

Digital gift cards with a spendable balance and an immutable transaction
ledger:

* ``GiftCard``            — a redeemable card with ``balance`` / ``status``.
* ``GiftCardTransaction`` — an audit entry (issue/redeem/reload/void).

All models carry the standard sync-tracking fields (``is_synced`` /
``synced_at`` / ``sync_status``) so they participate in the multi-terminal
changeset collector alongside the rest of the pos_full app.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class GiftCard(models.Model):
    """A digital gift card with a spendable balance."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("used", "Used"),
        ("expired", "Expired"),
        ("disabled", "Disabled"),
    ]

    code = models.CharField(max_length=40, unique=True)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Remaining spendable balance.",
    )
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True,
    )
    recipient_name = models.CharField(max_length=200, blank=True, default="")
    recipient_email = models.EmailField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
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
        db_table = "full_gift_cards"
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["status", "expires_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} ({self.balance}/{self.initial_balance})"


class GiftCardTransaction(models.Model):
    """Immutable ledger entry for a gift card balance movement."""

    TX_TYPES = [
        ("issue", "Issue"),
        ("redeem", "Redeem"),
        ("reload", "Reload"),
        ("void", "Void"),
    ]

    gift_card = models.ForeignKey(
        GiftCard, on_delete=models.CASCADE, related_name="transactions",
    )
    transaction_type = models.CharField(max_length=20, choices=TX_TYPES)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Signed amount: positive = adds balance, negative = spends.",
    )
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    sale = models.ForeignKey(
        "Sale", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="gift_card_transactions",
        help_text="Sale this redemption was applied to (redeem only).",
    )
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
        db_table = "full_gift_card_transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["gift_card", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.transaction_type} {self.amount} → {self.gift_card.code}"
