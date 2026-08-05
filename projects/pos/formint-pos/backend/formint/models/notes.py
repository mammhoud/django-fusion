"""
POS Full — Notes model.

Stores user notes with draft/save/archive status.  Notes can reference
cart, inventory, or count actions via reference_type + reference_id
for context-aware note-taking and draft restoration.

Table: full_notes
"""

from __future__ import annotations

from django.db import models


class Note(models.Model):
    """User note with draft save/restore capability.

    Notes can be linked to cart actions, inventory counts, or other
    POS entities so users can take notes during operations and restore
    them later from the same screen.
    """

    STATUS_CHOICES = [
        ("draft", "Draft — not yet finalised"),
        ("saved", "Saved — completed note"),
        ("archived", "Archived — hidden from default view"),
    ]

    REFERENCE_TYPES = [
        ("", "General — no specific reference"),
        ("cart", "Cart action — linked to a check-out / sale cart"),
        ("inventory", "Inventory — linked to a stock count or adjustment"),
        ("count", "Physical count — linked to a stock-take event"),
        ("order", "Order — linked to a purchase order"),
        ("customer", "Customer — linked to a customer record"),
    ]

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Optional short title for the note",
    )
    content = models.TextField(
        blank=True,
        default="",
        help_text="Full note body — supports multiline text",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True,
    )
    reference_type = models.CharField(
        max_length=30,
        choices=REFERENCE_TYPES,
        blank=True,
        default="",
        help_text="Entity type this note is linked to (cart, inventory, count, …)",
    )
    reference_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="PK of the referenced entity (e.g. Sale.id, InventoryTransaction.id)",
    )
    created_by = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="User / device ID that created this note",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "formint"
        db_table = "full_notes"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "reference_type"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self) -> str:
        preview = self.title or (self.content[:50] + "…" if self.content else "(empty)")
        return f"[{self.status}] {preview}"
