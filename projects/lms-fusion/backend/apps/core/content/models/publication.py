"""
Fusion CMS — Publication model (Wagtail snippet).

Serves: GET /apis/research/publications
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class PublicationCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    sort_order = models.IntegerField(default=0)

    panels = [
        FieldPanel("name"), FieldPanel("slug"),
        FieldPanel("description"), FieldPanel("sort_order"),
    ]

    class Meta:
        app_label = "content"
        verbose_name = _("publication category")
        verbose_name_plural = _("publication categories")
        ordering = ["sort_order", "name"]

    def __str__(self): return self.name


@register_snippet
class Publication(index.Indexed, models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    abstract = RichTextField(blank=True, default="", features=["bold", "italic", "link"])
    authors = models.CharField(max_length=500, blank=True, default="")
    category = models.ForeignKey(PublicationCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="publications")
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True, db_index=True)
    external_url = models.URLField(blank=True, default="")

    panels = [
        MultiFieldPanel([FieldPanel("title"), FieldPanel("slug"), FieldPanel("authors"), FieldPanel("category")], heading="Details"),
        FieldPanel("abstract"),
        MultiFieldPanel([FieldPanel("published_at"), FieldPanel("is_published"), FieldPanel("external_url")], heading="Publishing"),
    ]

    search_fields = [
        index.SearchField("title", boost=10),
        index.SearchField("abstract", boost=5),
        index.FilterField("is_published"),
    ]

    class Meta:
        app_label = "content"
        verbose_name = _("publication")
        verbose_name_plural = _("publications")
        ordering = ["-published_at"]

    def __str__(self): return self.title
