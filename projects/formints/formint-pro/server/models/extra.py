from __future__ import annotations

"""
POS Full — Extra managed models: Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment.

These are needed by the frontend RTK Query endpoints but were previously
handled only by the Rust backend (Tauri invoke). Adding them as Django
models enables REST API CRUD via the generic _register_crud factory.

Each model includes DataToken-sync fields (is_synced, synced_at, sync_status)
for cloud sync tracking, following the same pattern as models/pos.py.

Tables: full_ingredients, full_recipes, full_receipt_templates,
        full_roles, full_inventory_adjustments
"""

from django.db import models


# ===========================================================================
# Ingredient — raw material / stock item used in recipes
# ===========================================================================

class Ingredient(models.Model):
    """Raw ingredient used in recipes and inventory management."""

    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, help_text="e.g. kg, liter, piece")
    current_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
        db_table = "full_ingredients"
        ordering = ["name"]
        verbose_name_plural = "ingredients"

    def __str__(self) -> str:
        return f"{self.name} ({self.unit})"


# ===========================================================================
# Recipe — product recipes / bills of materials
# ===========================================================================

class Recipe(models.Model):
    """Recipe linking a product to its ingredient composition."""

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="recipes",
        help_text="The finished product this recipe produces",
    )
    name = models.CharField(max_length=200, blank=True, default="",
        help_text="Optional recipe name (auto-derived from product if empty)")
    instructions = models.TextField(blank=True, default="")
    yield_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=1,
        help_text="Number of units this recipe produces",
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
        db_table = "full_recipes"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name or f"Recipe for #{self.product_id}"

    def save(self, *args, **kwargs):
        if not self.name and self.product_id:
            try:
                from models.pos import Product
            except ImportError:
                return super().save(*args, **kwargs)
            try:
                prod = Product.objects.get(id=self.product_id)
                self.name = f"Recipe: {prod.name}"
            except Product.DoesNotExist:
                pass
        super().save(*args, **kwargs)


# ===========================================================================
# ReceiptTemplate — printable receipt/invoice layout templates
# ===========================================================================

class ReceiptTemplate(models.Model):
    """Customizable receipt and invoice print templates."""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, default="")
    template_html = models.TextField(
        blank=True, default="",
        help_text="HTML template with {{placeholders}} for dynamic fields",
    )
    template_css = models.TextField(
        blank=True, default="",
        help_text="CSS styles for the receipt layout",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default template used for new receipts",
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
        db_table = "full_receipt_templates"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


# ===========================================================================
# Role — user/employee roles with permissions
# ===========================================================================

class Role(models.Model):
    """Access control role for POS users."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    permissions = models.JSONField(
        default=dict, blank=True,
        help_text="JSON dict of permission flags, e.g. {\"can_manage_products\": true}",
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
        db_table = "full_roles"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


# ===========================================================================
# InventoryAdjustment — manual stock corrections
# ===========================================================================

class InventoryAdjustment(models.Model):
    """Manual adjustment to ingredient/stock quantities.

    Supports deltas (``quantity``) and snapshots (``previous_quantity`` / ``new_quantity``).
    If ``new_quantity`` is not provided, it is computed as ``previous_quantity + quantity``.
    """

    ADJUSTMENT_TYPES = [
        ("addition", "Addition — stock increased"),
        ("removal", "Removal — stock decreased"),
        ("adjustment", "Adjustment — manual correction"),
        ("transfer", "Transfer — moved between locations"),
    ]

    ADJUSTMENT_REASONS = [
        ("damage", "Damage / Spoilage"),
        ("loss", "Loss / Theft"),
        ("correction", "Inventory Correction"),
        ("return", "Return from Customer"),
        ("waste", "Waste / Disposal"),
        ("other", "Other"),
    ]

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="adjustments",
        help_text="Ingredient being adjusted",
    )

    # ── Delta (the actual change amount, positive or negative) ──
    quantity = models.DecimalField(
        max_digits=12, decimal_places=3, default=0,
        help_text="Change amount (positive = addition, negative = removal)",
    )
    adjustment_type = models.CharField(
        max_length=20, choices=ADJUSTMENT_TYPES, default="adjustment",
        help_text="Type of inventory adjustment",
    )

    # ── Snapshots (before/after state) ──
    previous_quantity = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True,
        help_text="Stock level before adjustment",
    )
    new_quantity = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True,
        help_text="Stock level after adjustment",
    )

    reason = models.CharField(max_length=20, choices=ADJUSTMENT_REASONS, default="correction")
    notes = models.TextField(blank=True, default="")
    created_by = models.CharField(max_length=100, blank=True, default="")
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
        db_table = "full_inventory_adjustments"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_adjustment_type_display()} — {self.ingredient.name}"

    def save(self, *args, **kwargs):
        """Auto-populate previous_quantity from ingredient, compute new_quantity from delta,
        and update the ingredient's live stock level (only on create, not PATCH)."""
        from decimal import Decimal as _D

        is_new_instance = self.pk is None
        qty = _D(str(self.quantity)) if isinstance(self.quantity, float) else self.quantity

        if self.previous_quantity is None and self.ingredient_id:
            try:
                ing = Ingredient.objects.get(id=self.ingredient_id)
                self.previous_quantity = ing.current_quantity
            except Ingredient.DoesNotExist:
                pass

        if self.new_quantity is None and qty != 0 and self.previous_quantity is not None:
            self.new_quantity = self.previous_quantity + qty

        super().save(*args, **kwargs)

        # ── Update the ingredient's live stock level (only on create, not PATCH) ──
        if is_new_instance and qty != 0 and self.ingredient_id:
            try:
                ing = Ingredient.objects.get(id=self.ingredient_id)
                ing.current_quantity = (
                    self.new_quantity
                    if self.new_quantity is not None
                    else ing.current_quantity + qty
                )
                ing.save(update_fields=["current_quantity", "updated_at"])
            except Ingredient.DoesNotExist:
                pass
