"""
Complete Django models mirroring the full Diesel/SQLite schema managed by Rust.
All 29 Rust-managed tables declared with managed=False so Django never creates
or alters them — the Rust side owns the schema via migrations.

SupportTicket is the single table Django does own (managed=True).

Related Names: django, models, orm, sqlite, schema, mirror, sidecar, managed
Tags: #django #models #sqlite #schema #sidecar
"""

from django.db import models


# ---------------------------------------------------------------------------
# RUST-MANAGED TABLES (read/query only via Django ORM)
# managed=False on every table — Rust owns the schema via Diesel migrations.
# ---------------------------------------------------------------------------

class AppSettings(models.Model):
    """Mirrors the `settings` table (singleton, id=1)."""
    restaurant_name = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    tax_rate = models.TextField(null=True, blank=True)
    currency = models.TextField(default="USD")
    opening_time = models.TextField(null=True, blank=True)
    closing_time = models.TextField(null=True, blank=True)
    receipt_footer = models.TextField(null=True, blank=True)
    logo = models.TextField(null=True, blank=True)
    dine_in_tables = models.IntegerField(default=0)
    delivery_fee = models.FloatField(default=0)
    delivery_fee_per_km = models.FloatField(default=0)

    class Meta:
        db_table = "settings"
        managed = False

    def __str__(self):
        return self.restaurant_name or "POS Settings"


class Category(models.Model):
    """Product categories (e.g., Burgers, Pizza, Beverages)."""
    name = models.TextField(unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "categories"
        managed = False
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Menu items for sale."""
    name = models.TextField()
    price = models.FloatField()
    unit = models.TextField(default="item")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, db_column="category_id")
    image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "products"
        managed = False
        ordering = ["category__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.price})"


class DeliveryType(models.Model):
    """Order delivery/pickup types."""
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    fee_multiplier = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "delivery_types"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmployeeType(models.Model):
    """Staff role categories (chef, waiter, manager, etc.)."""
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "employee_types"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Staff members."""
    name = models.TextField()
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, db_column="employee_type_id")
    salary = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    joined_at = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "employees"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Customer CRM with loyalty points."""
    name = models.TextField()
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    loyalty_points = models.FloatField(default=0)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "customers"
        managed = False
        ordering = ["-loyalty_points", "name"]

    def __str__(self):
        return self.name


class Sale(models.Model):
    """Transaction header — a complete order."""
    total_amount = models.FloatField()
    currency = models.TextField(default="USD")
    date = models.TextField()
    time = models.TextField()
    order_type = models.TextField(default="dine_in")
    status = models.TextField(default="completed")
    table_number = models.IntegerField(null=True, blank=True)
    delivery_type = models.ForeignKey(DeliveryType, null=True, blank=True, on_delete=models.SET_NULL, db_column="delivery_type_id")
    delivery_address = models.TextField(null=True, blank=True)
    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, db_column="employee_id")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, db_column="customer_id")
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "sales"
        managed = False
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sale #{self.id} — {self.total_amount}"


class SaleItem(models.Model):
    """Line items within a sale."""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="line_items", db_column="sale_id")
    product_name = models.TextField()
    price = models.FloatField()
    quantity = models.FloatField()
    unit = models.TextField()
    subtotal = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "sale_items"
        managed = False

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class Ingredient(models.Model):
    """Raw materials / stock items."""
    name = models.TextField(unique=True)
    unit = models.TextField()
    current_quantity = models.FloatField(default=0.0)
    reorder_level = models.FloatField(default=0.0)
    reorder_quantity = models.FloatField(default=0.0)
    cost_per_unit = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "ingredients"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return self.name


class RecipeType(models.Model):
    """Recipe classification (standard, special, seasonal)."""
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "recipe_types"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Links a product to its ingredient bill-of-materials."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="product_id")
    recipe_type = models.ForeignKey(RecipeType, on_delete=models.CASCADE, db_column="recipe_type_id")
    yield_quantity = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "recipes"
        managed = False
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "recipe_ingredients"
        managed = False

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
    created_at = models.DateTimeField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "inventory_transactions"
        managed = False
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
    created_at = models.DateTimeField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "inventory_adjustments"
        managed = False
        ordering = ["-created_at"]


class InventoryAlert(models.Model):
    """Low-stock and other inventory alerts."""
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column="ingredient_id")
    alert_type = models.TextField(default="low_stock")
    alert_message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_alerts"
        managed = False
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "suppliers"
        managed = False
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "purchase_orders"
        managed = False
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
        db_table = "purchase_order_items"
        managed = False


class KitchenTicket(models.Model):
    """Kitchen display system tickets linked to sales."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
    ]
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, db_column="sale_id")
    status = models.TextField(default="pending", choices=STATUS_CHOICES)
    priority = models.IntegerField(default=0)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "kitchen_tickets"
        managed = False
        ordering = ["-priority", "created_at"]

    def __str__(self):
        return f"Ticket #{self.id} — Sale #{self.sale_id}"


class LoyaltyTransaction(models.Model):
    """Customer loyalty points ledger."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column="customer_id")
    sale = models.ForeignKey(Sale, null=True, blank=True, on_delete=models.SET_NULL, db_column="sale_id")
    points_change = models.FloatField()
    reason = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "loyalty_transactions"
        managed = False
        ordering = ["-created_at"]


class ReceiptTemplate(models.Model):
    """Customizable receipt body templates."""
    name = models.TextField()
    template_body = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "receipt_templates"
        managed = False
        ordering = ["-is_default", "name"]

    def __str__(self):
        return self.name


class TaxReport(models.Model):
    """Periodic tax summaries."""
    period_start = models.TextField()
    period_end = models.TextField()
    total_sales = models.FloatField()
    total_tax = models.FloatField()
    transaction_count = models.IntegerField()
    generated_at = models.DateTimeField()

    class Meta:
        db_table = "tax_reports"
        managed = False
        ordering = ["-period_start"]


class EmployeeSchedule(models.Model):
    """Employee shift schedules."""
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("absent", "Absent"),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column="employee_id")
    shift_start = models.DateTimeField()
    shift_end = models.DateTimeField()
    status = models.TextField(default="scheduled", choices=STATUS_CHOICES)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "employee_schedules"
        managed = False
        ordering = ["-shift_start"]


class Payroll(models.Model):
    """Employee payslips."""
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("paid", "Paid"),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column="employee_id")
    period_start = models.TextField()
    period_end = models.TextField()
    regular_hours = models.FloatField()
    overtime_hours = models.FloatField()
    total_pay = models.FloatField()
    status = models.TextField(default="draft", choices=STATUS_CHOICES)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "payrolls"
        managed = False
        ordering = ["-period_start"]


class User(models.Model):
    """POS user accounts (Rust-managed, not Django auth.User)."""
    email = models.TextField(unique=True)
    password_hash = models.TextField()
    name = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "users"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Role(models.Model):
    """RBAC roles with JSON permission sets."""
    name = models.TextField(unique=True)
    permissions = models.TextField(default="[]")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "roles"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Many-to-many join: users ↔ roles."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role_id")
    created_at = models.DateTimeField()

    class Meta:
        db_table = "user_roles"
        managed = False
        unique_together = [("user_id", "role_id")]


class ReportMetadata(models.Model):
    """Generated report file metadata."""
    report_type = models.TextField()
    format = models.TextField()
    file_path = models.TextField()
    parameters = models.TextField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, db_column="generated_by")
    created_at = models.DateTimeField()

    class Meta:
        db_table = "report_metadata"
        managed = False
        ordering = ["-created_at"]


# ---------------------------------------------------------------------------
# DJANGO-MANAGED TABLE (managed=True — owned by this app)
# ---------------------------------------------------------------------------

class SupportTicket(models.Model):
    """Customer/user support tickets submitted via the in-app chat widget."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    name = models.TextField()
    email = models.TextField()
    subject = models.TextField()
    message = models.TextField()
    status = models.TextField(default="open", choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "support_tickets"
        managed = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.status}] {self.subject} — {self.name}"
