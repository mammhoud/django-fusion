"""CTC Research — Blog, Event, Testimonial model stubs for bolt API."""

from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class BlogPost(index.Indexed, models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    excerpt = models.TextField(blank=True, default="")
    content = models.TextField(blank=True, default="")
    author = models.CharField(max_length=200, blank=True, default="")
    category = models.JSONField(default=dict, blank=True)
    featured_image = models.ForeignKey("wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True, db_index=True)

    panels = [
        MultiFieldPanel([FieldPanel("title"), FieldPanel("slug"), FieldPanel("author"), FieldPanel("category")], heading="Post Details"),
        FieldPanel("excerpt"), FieldPanel("content"),
        MultiFieldPanel([FieldPanel("featured_image"), FieldPanel("published_at"), FieldPanel("is_published")], heading="Publishing"),
    ]

    search_fields = [index.SearchField("title", boost=10), index.SearchField("excerpt", boost=5), index.FilterField("is_published")]

    class Meta:
        app_label = "content"
        verbose_name = "blog post"
        verbose_name_plural = "blog posts"
        ordering = ["-published_at"]

    def __str__(self): return self.title


@register_snippet
class Event(index.Indexed, models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField(blank=True, default="")
    location = models.CharField(max_length=300, blank=True, default="")
    event_date = models.DateTimeField(null=True, blank=True)
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    is_published = models.BooleanField(default=True, db_index=True)

    panels = [
        FieldPanel("title"), FieldPanel("slug"), FieldPanel("description"),
        FieldPanel("location"), FieldPanel("event_date"), FieldPanel("image"), FieldPanel("is_published"),
    ]

    search_fields = [index.SearchField("title", boost=10), index.FilterField("is_published")]

    class Meta:
        app_label = "content"
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = ["event_date"]

    def __str__(self): return self.title


@register_snippet
class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, blank=True, default="")
    quote = models.TextField(blank=True, default="")
    avatar = models.ForeignKey("wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.IntegerField(default=0)

    panels = [
        FieldPanel("name"), FieldPanel("designation"), FieldPanel("quote"),
        FieldPanel("avatar"), FieldPanel("rating"), FieldPanel("is_active"), FieldPanel("sort_order"),
    ]

    class Meta:
        app_label = "content"
        verbose_name = "testimonial"
        verbose_name_plural = "testimonials"
        ordering = ["sort_order"]

    def __str__(self): return f"{self.name} — {self.designation}"
