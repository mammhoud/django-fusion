# Django ORM models mirroring Rust/Diesel schema (managed=True for Solo, app_label="posapp")

from django.db import models


class AppSettings(models.Model):
    """POS application settings (singleton, id=1)."""
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
        app_label = "posapp"
        db_table = "settings"
        managed = True

    def __str__(self):
        return self.restaurant_name or "POS Settings"


class Category(models.Model):
    """Product categories (e.g., Burgers, Pizza, Beverages)."""
    name = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "categories"
        managed = True
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)

    class Meta:
        app_label = "posapp"
        db_table = "products"
        managed = True
        ordering = ["category__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.price})"


class DeliveryType(models.Model):
    """Order delivery/pickup types."""
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    fee_multiplier = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "delivery_types"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmployeeType(models.Model):
    """Staff role categories (chef, waiter, manager, etc.)."""
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "employee_types"
        managed = True
        ordering = ["name"]

    def __str__(self):
        return self.name
