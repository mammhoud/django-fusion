"""
Cart and CartItem models for the products plugin.

Cart supports both authenticated users (DB-backed) and anonymous
visitors (session-backed via CartService).
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Cart(models.Model):
    """
    Persistent shopping cart.

    Linked to a user when authenticated, or to a session key for guests.
    On login the session cart is merged into the user cart by CartService.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
        verbose_name=_("user"),
    )
    session_key = models.CharField(
        _("session key"),
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        app_label = "products"
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        constraints = [
            models.UniqueConstraint(
                fields=["session_key"],
                condition=models.Q(session_key__isnull=False),
                name="products_cart_unique_session",
            )
        ]

    def __str__(self) -> str:
        if self.user:
            return f"Cart({self.user.email})"
        return f"Cart(session={self.session_key})"

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def total_items(self) -> int:
        """Total number of individual units across all line items."""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self) -> Decimal:
        """Grand total of all line items."""
        return sum(item.total_price for item in self.items.all()) or Decimal("0.00")


class CartItem(models.Model):
    """
    A single line item inside a Cart.

    Stores a generic product reference (name + price snapshot) so the cart
    works with any product type.  Specialised apps (e.g. LMS) can subclass
    this to add a FK to their own product model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("cart"),
    )
    # Generic product snapshot — always populated
    product_id = models.CharField(
        _("product ID"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Opaque identifier from the originating product catalogue."),
    )
    product_name = models.CharField(_("product name"), max_length=255)
    product_description = models.TextField(_("product description"), blank=True)
    price = models.DecimalField(
        _("unit price"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    added_at = models.DateTimeField(_("added at"), auto_now_add=True)

    class Meta:
        app_label = "products"
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ["added_at"]

    def __str__(self) -> str:
        return f"{self.product_name} × {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        return self.price * self.quantity
