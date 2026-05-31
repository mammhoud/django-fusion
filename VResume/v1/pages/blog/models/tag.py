"""
BlogPageTag — through model linking BlogTag to BlogPage.
BlogTag itself lives in snippets/tag.py (managed as a snippet).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel
from wagtail.models import Orderable

from .snippets.tag import BlogTag


class BlogPageTag(Orderable):
    """
    Through model: BlogPage ↔ BlogTag.
    Shown in the Tags tab of BlogPage's TabbedInterface.
    """
    page = ParentalKey(
        "blog.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )
    tag = models.ForeignKey(
        BlogTag,
        on_delete=models.CASCADE,
        related_name="blog_pages",
        verbose_name=_("Tag"),
    )
    is_primary = models.BooleanField(default=False, verbose_name=_("Primary Tag"))

    panels = [
        FieldPanel("tag"),
        FieldPanel("is_primary"),
    ]

    class Meta:
        verbose_name = _("Blog Page Tag")
        verbose_name_plural = _("Blog Page Tags")
        ordering = ["-is_primary", "sort_order"]
        unique_together = [["page", "tag"]]
        app_label = "blog"

    def __str__(self):
        return f"{self.page.title} — {self.tag.name}"
