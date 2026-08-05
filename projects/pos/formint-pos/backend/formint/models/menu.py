"""
POS Solo menu models — MenuItem, Menu, MenuItemAssignment.
"""

from __future__ import annotations

from django.db import models


from formint.models.pos import Category


class MenuItem(models.Model):
    """Menu item — a product available on a specific menu."""

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="menu_items",
    )
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, blank=True)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    preparation_time = models.IntegerField(blank=True, null=True)
    ingredients = models.TextField(blank=True, default="")
    allergens = models.CharField(max_length=500, blank=True, default="")
    calories = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "formint"
        db_table = "full_menu_items"
        ordering = ["category__display_order", "display_order", "name"]

    def __str__(self) -> str:
        return f"{self.name} (${self.price})"


class Menu(models.Model):
    """Named menu — curated collection of items."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    items = models.ManyToManyField(MenuItem, through="MenuItemAssignment", related_name="menus")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "formint"
        db_table = "full_menus"
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class MenuItemAssignment(models.Model):
    """Through model linking menus to items with optional override price."""

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    override_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
    )
    display_order = models.IntegerField(default=0)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "formint"
        db_table = "full_menu_assignments"
        ordering = ["display_order"]

    def __str__(self) -> str:
        return f"{self.item.name} → {self.menu.name}"
