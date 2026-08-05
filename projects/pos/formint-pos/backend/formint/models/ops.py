"""
POS Full — managed operations models.

Managed Django ORM models (app_label="pos_full").
Replaces the previously deleted posapp Rust-mirror models.
"""

from __future__ import annotations

from django.db import models


class KitchenTicket(models.Model):
    """Kitchen display system tickets linked to sales."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
    ]

    sale = models.ForeignKey(
        "Sale", on_delete=models.CASCADE, related_name="kitchen_tickets"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.IntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "formint"
        db_table = "full_kitchen_tickets"
        ordering = ["-priority", "created_at"]

    def __str__(self) -> str:
        return f"Kitchen Ticket #{self.id} — Sale #{self.sale_id}"


class SupportTicket(models.Model):
    """Customer/user support tickets submitted via the in-app chat widget."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "formint"
        db_table = "full_support_tickets"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.status}] {self.subject} — {self.name}"
