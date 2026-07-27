"""Fusion Branding — a reusable Wagtail snippet for site/company
branding settings.

Register as a snippet and use the ``fusion_branding_context`` context
processor to inject branding into templates.

Requires Wagtail.
"""

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class FusionBranding(models.Model):
    """Wagtail snippet holding site/company branding settings.

    Create a single instance and it will be picked up automatically
    by the ``fusion_branding_context`` context processor.

    Example usage in templates::

        {{ fusion_branding.site_name }}
        {{ fusion_branding.primary_color }}
    """

    site_name = models.CharField(max_length=100, default="Fusion")
    company_name = models.CharField(max_length=100, default="Fusion Inc.")
    creator_name = models.CharField(max_length=100, default="Fusion Team")
    primary_color = models.CharField(max_length=7, default="#00a1b3")
    favicon = models.ImageField(upload_to="branding/", blank=True)

    panels = [
        FieldPanel("site_name"),
        FieldPanel("company_name"),
        FieldPanel("creator_name"),
        FieldPanel("primary_color"),
        FieldPanel("favicon"),
    ]

    class Meta:
        verbose_name = "Fusion Branding"
        verbose_name_plural = "Fusion Brandings"

    def __str__(self):
        return self.site_name
