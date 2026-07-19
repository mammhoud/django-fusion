"""
Shared models for POS Portal editions.
Provides base MenuItem, Category, and Menu models used across
all editions (vresume, solo, minimal, full).

@tested pos-portal/shared - Base models used by all editions
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Menu category - groups menu items (e.g., Appetizers, Main Course, Drinks)."""

    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    description = models.TextField(_("description"), blank=True)
    display_order = models.IntegerField(_("display order"), default=0)
    is_active = models.BooleanField(_("active"), default=True)
    image = models.ImageField(_("image"), upload_to="portal/categories/", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class MenuItem(models.Model):
    """Individual menu item - a product or dish available for order."""

    CURRENCY_CHOICES = [
        ("USD", "USD"),
        ("EUR", "EUR"),
        ("GBP", "GBP"),
        ("PKR", "PKR"),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("category"),
    )
    name = models.CharField(_("name"), max_length=300)
    slug = models.SlugField(_("slug"), max_length=300)
    description = models.TextField(_("description"), blank=True)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    currency = models.CharField(
        _("currency"), max_length=3, choices=CURRENCY_CHOICES, default="USD"
    )
    is_available = models.BooleanField(_("available"), default=True)
    is_featured = models.BooleanField(_("featured"), default=False)
    display_order = models.IntegerField(_("display order"), default=0)
    image = models.ImageField(_("image"), upload_to="portal/items/", blank=True)
    preparation_time = models.IntegerField(
        _("preparation time (minutes)"), blank=True, null=True
    )
    ingredients = models.TextField(_("ingredients"), blank=True)
    allergens = models.CharField(_("allergens"), max_length=500, blank=True)
    calories = models.IntegerField(_("calories"), blank=True, null=True)

    # External reference — links to POS SQLite product ID (read-only sync)
    pos_product_id = models.IntegerField(
        _("POS product ID"), blank=True, null=True, editable=False
    )
    pos_synced_at = models.DateTimeField(
        _("last POS sync"), blank=True, null=True, editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("menu item")
        verbose_name_plural = _("menu items")
        ordering = ["category__display_order", "display_order", "name"]
        unique_together = [("category", "slug")]

    def __str__(self) -> str:
        return f"{self.name} ({self.currency} {self.price})"


class Menu(models.Model):
    """Named menu - a curated collection of items (e.g., Lunch Menu, Dinner Menu)."""

    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    description = models.TextField(_("description"), blank=True)
    items = models.ManyToManyField(
        MenuItem, through="MenuItemAssignment", related_name="menus"
    )
    is_active = models.BooleanField(_("active"), default=True)
    valid_from = models.DateTimeField(_("valid from"), blank=True, null=True)
    valid_until = models.DateTimeField(_("valid until"), blank=True, null=True)
    display_order = models.IntegerField(_("display order"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("menu")
        verbose_name_plural = _("menus")
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class MenuItemAssignment(models.Model):
    """Through model: item within a menu with optional override price."""

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    override_price = models.DecimalField(
        _("override price"), max_digits=10, decimal_places=2,
        blank=True, null=True,
        help_text=_("If set, overrides the item's base price for this menu"),
    )
    display_order = models.IntegerField(_("display order"), default=0)

    class Meta:
        verbose_name = _("menu item assignment")
        verbose_name_plural = _("menu item assignments")
        ordering = ["display_order"]

    def __str__(self) -> str:
        return f"{self.item.name} → {self.menu.name}"
