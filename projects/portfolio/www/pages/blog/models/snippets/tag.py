"""
BlogTag — managed as a snippet in the admin.
Tags are created/edited via the Blog > Tags viewset.
BlogPage and BlogPost select tags via M2M / InlinePanel.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


class BlogTag(models.Model):
    """
    Tag for blog posts and snippets.
    Category grouping is a plain CharField on the tag itself.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    category = models.CharField(
        max_length=100, blank=True,
        verbose_name=_("Category"),
        help_text=_("Group tags by category, e.g. Technology, Design"),
    )
    color = models.CharField(max_length=7, default="#ee9b00", verbose_name=_("Color"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon Class"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("category"),
        FieldPanel("color"),
        FieldPanel("icon"),
        FieldPanel("display_order"),
        FieldPanel("is_active"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("description"),
        index.SearchField("category"),
    ]

    class Meta:
        verbose_name = _("Blog Tag")
        verbose_name_plural = _("Blog Tags")
        ordering = ["display_order", "name"]
        indexes = [models.Index(fields=["category", "is_active"])]
        app_label = "blog"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
