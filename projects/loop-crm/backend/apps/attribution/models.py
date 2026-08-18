"""Loop-CRM attribution module — the RevOps glue.

AttributionTouchpoint records every marketing interaction that led to a deal;
AttributionModel selects the weighting strategy (first/last touch, linear,
time-decay, position-based). The calculator (engines/calculator.py) rewrites
each touchpoint's weight so revenue can be attributed back to campaigns.
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import Workspace


class AttributionModel(models.Model):
    """A named, workspace-scoped attribution strategy."""

    MODEL_TYPES = [
        ("first_touch", _("First Touch")),
        ("last_touch", _("Last Touch")),
        ("linear", _("Linear")),
        ("time_decay", _("Time Decay")),
        ("position_based", _("Position Based")),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="attribution_models")
    name = models.CharField(max_length=255, verbose_name=_("name"))
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES, default="linear", verbose_name=_("model type"))
    is_active = models.BooleanField(default=False, verbose_name=_("is active"))
    config = models.JSONField(default=dict, verbose_name=_("config"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    class Meta:
        ordering = ["name"]
        verbose_name = _("attribution model")
        verbose_name_plural = _("attribution models")

    def __str__(self) -> str:
        return self.name


class AttributionTouchpoint(models.Model):
    """One marketing interaction credited (fractionally) toward a deal."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="touchpoints", verbose_name=_("workspace"))
    deal = models.ForeignKey("crm.Deal", on_delete=models.CASCADE, related_name="touchpoints", verbose_name=_("deal"))
    post = models.ForeignKey("marketing.Post", on_delete=models.SET_NULL, null=True, blank=True, related_name="touchpoints", verbose_name=_("post"))
    campaign = models.ForeignKey("marketing.Campaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="touchpoints", verbose_name=_("campaign"))
    source = models.CharField(max_length=50, default="post", verbose_name=_("source"))
    occurred_at = models.DateTimeField(verbose_name=_("occurred at"))
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_("weight"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        ordering = ["occurred_at"]
        verbose_name = _("attribution touchpoint")
        verbose_name_plural = _("attribution touchpoints")
        indexes = [
            models.Index(fields=["workspace", "deal"]),
            models.Index(fields=["workspace", "campaign"]),
        ]

    def __str__(self) -> str:
        return f"{self.source} → {self.deal}"
