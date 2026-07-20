# Django ORM models mirroring Rust/Diesel schema (managed=True for Solo, app_label="posapp")

from django.db import models

from models.core import Product


class Ingredient(models.Model):
    """Raw materials / stock items."""
    name = models.TextField(unique=True)
    unit = models.TextField()
    current_quantity = models.FloatField(default=0.0)
    reorder_level = models.FloatField(default=0.0)
    reorder_quantity = models.FloatField(default=0.0)
    cost_per_unit = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)

    class Meta:
        app_label = "posapp"
        db_table = "ingredients"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class RecipeType(models.Model):
    """Recipe classification (standard, special, seasonal)."""
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "recipe_types"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Links a product to its ingredient bill-of-materials."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="product_id")
    recipe_type = models.ForeignKey(RecipeType, on_delete=models.CASCADE, db_column="recipe_type_id")
    yield_quantity = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)

    class Meta:
        app_label = "posapp"
        db_table = "recipes"
        managed = True
        unique_together = [("product_id", "recipe_type_id")]
        ordering = ["product__name"]

    def __str__(self):
        return f"Recipe for {self.product.name}"


class RecipeIngredient(models.Model):
    """Individual ingredient within a recipe."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, db_column="recipe_id")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ingredient_id")
    quantity = models.FloatField()
    unit = models.TextField(null=True, blank=True)
    preparation_note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "recipe_ingredients"
        managed = True

    def __str__(self):
        return f"{self.ingredient.name} in {self.recipe}"


class InventoryTransaction(models.Model):
    """Stock movements: purchase, usage, waste, adjustment, return."""
    TRANSACTION_TYPES = [
        ("purchase", "Purchase"),
        ("usage", "Usage"),
        ("waste", "Waste"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
    ]
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ingredient_id")
    transaction_type = models.TextField(choices=TRANSACTION_TYPES)
    quantity_change = models.FloatField()
    reference_id = models.IntegerField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded = models.BooleanField(default=False)

    class Meta:
        app_label = "posapp"
        db_table = "inventory_transactions"
        managed = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} {self.ingredient.name} ({self.quantity_change})"


class InventoryAdjustment(models.Model):
    """Manual stock corrections."""
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ingredient_id")
    previous_quantity = models.FloatField()
    new_quantity = models.FloatField()
    reason = models.TextField()
    created_by = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded = models.BooleanField(default=False)

    class Meta:
        app_label = "posapp"
        db_table = "inventory_adjustments"
        managed = True
        ordering = ["-created_at"]


class InventoryAlert(models.Model):
    """Low-stock and other inventory alerts."""
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ingredient_id")
    alert_type = models.TextField(default="low_stock")
    alert_message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "posapp"
        db_table = "inventory_alerts"
        managed = True
        ordering = ["-created_at"]


class Supplier(models.Model):
    """Vendors / suppliers for ingredients."""
    name = models.TextField()
    contact_name = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    tax_id = models.TextField(null=True, blank=True)
    payment_terms = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "suppliers"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    """Procurement orders from suppliers."""
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("ordered", "Ordered"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, db_column="supplier_id")
    reference_number = models.TextField(null=True, blank=True)
    status = models.TextField(default="draft", choices=STATUS_CHOICES)
    total_amount = models.FloatField(default=0)
    expected_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "purchase_orders"
        managed = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"PO #{self.id} — {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    """Line items within a purchase order."""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, db_column="purchase_order_id")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ingredient_id")
    quantity = models.FloatField()
    cost_per_unit = models.FloatField()
    received_quantity = models.FloatField(default=0)

    class Meta:
        app_label = "posapp"
        db_table = "purchase_order_items"
        managed = True
