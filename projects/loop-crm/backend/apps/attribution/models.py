"""Loop-CRM attribution module — the RevOps glue.

AttributionTouchpoint records every marketing interaction that led to a deal;
AttributionModel selects the weighting strategy (first/last touch, linear,
time-decay, position-based). The calculator (engines/calculator.py) rewrites
each touchpoint's weight so revenue can be attributed back to campaigns.
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import Workspace


class AttributionModel(models.Model):
    """A named, workspace-scoped attribution strategy."""

    MODEL_TYPES = [
        ("first_touch", "First Touch"),
        ("last_touch", "Last Touch"),
        ("linear", "Linear"),
        ("time_decay", "Time Decay"),
        ("position_based", "Position Based"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="attribution_models")
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES, default="linear")
    is_active = models.BooleanField(default=False)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class AttributionTouchpoint(models.Model):
    """One marketing interaction credited (fractionally) toward a deal."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="touchpoints")
    deal = models.ForeignKey("crm.Deal", on_delete=models.CASCADE, related_name="touchpoints")
    post = models.ForeignKey("marketing.Post", on_delete=models.SET_NULL, null=True, blank=True, related_name="touchpoints")
    campaign = models.ForeignKey("marketing.Campaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="touchpoints")
    source = models.CharField(max_length=50, default="post")
    occurred_at = models.DateTimeField()
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["occurred_at"]
        indexes = [
            models.Index(fields=["workspace", "deal"]),
            models.Index(fields=["workspace", "campaign"]),
        ]

    def __str__(self) -> str:
        return f"{self.source} → {self.deal}"
