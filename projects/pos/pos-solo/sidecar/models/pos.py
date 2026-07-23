"""
POS Solo core models — Category, Product, Customer, Sale, SaleItem,
InventoryTransaction, Employee.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Product category — used by both Menu and POS Product systems."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_categories"
        verbose_name_plural = "categories"
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """POS product with pricing, stock, and tax information."""

    TAX_RATES = [
        ("exempt", "Tax Exempt"), ("standard", "Standard Rate"),
        ("reduced", "Reduced Rate"),
    ]

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.CharField(max_length=20, choices=TAX_RATES, default="standard")
    barcode = models.CharField(max_length=100, blank=True, default="")
    is_active = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    description = models.TextField(blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    border_color = models.CharField(max_length=7, blank=True, default="",
        help_text="Hex border color for product card display (e.g., #6366f1)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_products"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} (${self.price})"


class Customer(models.Model):
    """Customer record with loyalty and purchase history."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    loyalty_points = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_customers"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email or "Unknown"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Sale(models.Model):
    """POS transaction record."""

    PAYMENT_METHODS = [
        ("cash", "Cash"), ("card", "Card"), ("mobile", "Mobile"),
        ("mixed", "Mixed"), ("credit", "Store Credit"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"), ("completed", "Completed"),
        ("refunded", "Refunded"), ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sales",
    )
    sale_date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cashback_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text="Cashback/reward amount applied to this sale")
    total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cash")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_sales"
        ordering = ["-sale_date"]

    def __str__(self) -> str:
        return f"Sale #{self.id} — ${self.total}"


class SaleItem(models.Model):
    """Line item within a sale."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True, default="")
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_sale_items"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_name}"


class InventoryTransaction(models.Model):
    """Stock movement record."""

    TRANSACTION_TYPES = [
        ("in", "Stock In"), ("out", "Stock Out"),
        ("adjustment", "Adjustment"), ("return", "Return"),
        ("transfer_out", "Transfer Out (to other inventory)"),
        ("transfer_in", "Transfer In (from other inventory)"),
        ("waste", "Waste / Disposal"),
        ("restock", "Restock (from return)"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_by = models.CharField(max_length=100, blank=True, default="")
    # Multi-inventory support
    inventory_id = models.CharField(max_length=50, blank=True, default="main", db_index=True,
        help_text="Inventory/location identifier. 'main' = primary stock.")
    transfer_to_inventory = models.CharField(max_length=50, blank=True, default="",
        help_text="Target inventory ID for transfer_out transactions (pos-full only).")
    created_at = models.DateTimeField(auto_now_add=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_inventory"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()} — {self.product.name} x{self.quantity}"


class Employee(models.Model):
    """Staff member record."""

    ROLES = [
        ("cashier", "Cashier"), ("server", "Server"),
        ("manager", "Manager"), ("admin", "Administrator"),
        ("kitchen", "Kitchen Staff"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    role = models.CharField(max_length=20, choices=ROLES, default="cashier")
    pin_code = models.CharField(max_length=6, blank=True, default="")
    is_active = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_employees"
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"
