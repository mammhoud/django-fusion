# Django ORM models mirroring Rust/Diesel schema (managed=True for Solo, app_label="posapp")

from django.db import models

from models.core import DeliveryType
from models.people import Employee


class Customer(models.Model):
    """Customer CRM with loyalty points."""
    name = models.TextField()
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    loyalty_points = models.FloatField(default=0)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "customers"
        managed = True
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)

    class Meta:
        app_label = "posapp"
        db_table = "sales"
        managed = True
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "posapp"
        db_table = "sale_items"
        managed = True

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class LoyaltyTransaction(models.Model):
    """Customer loyalty points ledger."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column="customer_id")
    sale = models.ForeignKey(Sale, null=True, blank=True, on_delete=models.SET_NULL, db_column="sale_id")
    points_change = models.FloatField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "posapp"
        db_table = "loyalty_transactions"
        managed = True
        ordering = ["-created_at"]
