"""
Portfolio Tag Model
Tags for categorizing portfolio projects
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


class PortfolioTag(models.Model):
    """
    Reusable tag for portfolio projects.
    Managed via PortfolioTagViewSet in viewsets/tag.py
    
    Features:
    - Color coding for visual distinction
    - Icon support (Bootstrap icons)
    - Active/inactive status
    - Full search indexing
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Tag Name"),
        help_text=_("e.g., React, Django, UI Design, Mobile App")
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly version of the tag name")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Optional description of this tag")
    )
    color = models.CharField(
        max_length=7,
        default="#ee9b00",
        verbose_name=_("Tag Color"),
        help_text=_("Hex color code for the tag badge")
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon Class"),
        help_text=_("Bootstrap icon class, e.g., bi-code-square")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this tag is available for use")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("color"),
        FieldPanel("icon"),
        FieldPanel("is_active"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("description"),
    ]

    class Meta:
        verbose_name = _("Portfolio Tag")
        verbose_name_plural = _("Portfolio Tags")
        ordering = ["name"]
        app_label = 'portfolio'

    def __str__(self):
        return self.name
