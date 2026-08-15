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
    # Loyalty tier (people as a client category) — points-driven segmentation
    client_category = models.ForeignKey(
        "ClientCategory", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="customers",
        help_text="Client category / loyalty tier this customer belongs to",
    )
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default="")
    marketing_consent = models.BooleanField(
        default=False,
        help_text="Customer consented to marketing communications (GDPR).",
    )
    consent_granted_at = models.DateTimeField(null=True, blank=True)
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
    # ── Split-bill support (Mobile Waiter P1) ──
    # ``group`` links a sale to its table/session group; ``parent_sale`` marks
    # a sale as a split child of the original (parent) sale.
    group = models.ForeignKey(
        "SaleGroup", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sales",
    )
    parent_sale = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="children",
    )
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


class SaleGroup(models.Model):
    """A table/session grouping of related sales for split-bill workflows.

    Mobile Waiter P1: a waiter opens a group for a table, adds items, and
    splits the bill into child sales (each payable separately). ``group_key``
    is a stable idempotency/session key; child sales link back via
    ``Sale.group`` / ``Sale.parent_sale``.
    """

    ORDER_TYPES = [
        ("dine-in", "Dine In"),
        ("takeaway", "Takeaway"),
        ("delivery", "Delivery"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    group_key = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=200, default="", blank=True)
    table_number = models.CharField(max_length=50, default="", blank=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default="dine-in")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_sale_groups"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name or self.group_key} [{self.status}]"

    @property
    def total(self):
        return sum((sale.total or 0) for sale in self.sales.all())


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
    # Shipping / handling fee applied to this goods transaction
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text="Shipping or handling fee for this goods transaction.")
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
