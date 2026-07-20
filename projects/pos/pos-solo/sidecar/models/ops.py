# Django ORM models mirroring Rust/Diesel schema (managed=True for Solo, app_label="posapp")

from django.db import models

from models.people import User
from models.sales import Sale


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
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "posapp"
        db_table = "kitchen_tickets"
        managed = True
        ordering = ["-priority", "created_at"]

    def __str__(self):
        return f"Ticket #{self.id} — Sale #{self.sale_id}"


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
        app_label = "posapp"
        db_table = "support_tickets"
        managed = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.subject} — {self.name}"


class ReceiptTemplate(models.Model):
    """Customizable receipt body templates."""
    name = models.TextField()
    template_body = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "posapp"
        db_table = "receipt_templates"
        managed = True
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
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "posapp"
        db_table = "tax_reports"
        managed = True
        ordering = ["-period_start"]


class ReportMetadata(models.Model):
    """Generated report file metadata."""
    report_type = models.TextField()
    format = models.TextField()
    file_path = models.TextField()
    parameters = models.TextField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, db_column="generated_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "posapp"
        db_table = "report_metadata"
        managed = True
        ordering = ["-created_at"]
