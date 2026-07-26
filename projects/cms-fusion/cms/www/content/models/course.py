"""
CTC Research — Course model (Wagtail snippet).

Serves: GET /apis/courses
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class DifficultyChoices(models.TextChoices):
    BEGINNER = "beginner", _("Beginner")
    INTERMEDIATE = "intermediate", _("Intermediate")
    ADVANCED = "advanced", _("Advanced")
    ALL_LEVELS = "all_levels", _("All Levels")


@register_snippet
class Course(index.Indexed, models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = RichTextField(blank=True, default="", features=["bold", "italic", "link", "ol", "ul"])
    short_description = models.CharField(max_length=255, blank=True, default="")
    category = models.ForeignKey("CourseCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    skill_level = models.CharField(max_length=20, choices=DifficultyChoices.choices, default=DifficultyChoices.BEGINNER)
    language = models.CharField(max_length=50, default="English")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    instructor = models.CharField(max_length=200, blank=True, default="")
    duration = models.CharField(max_length=50, blank=True, default="")
    enrolled_count = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    panels = [
        MultiFieldPanel([FieldPanel("title"), FieldPanel("slug"), FieldPanel("short_description"), FieldPanel("category"), FieldPanel("skill_level"), FieldPanel("language")], heading="Details"),
        FieldPanel("description"),
        MultiFieldPanel([FieldPanel("price"), FieldPanel("instructor"), FieldPanel("duration")], heading="Pricing"),
        MultiFieldPanel([FieldPanel("rating"), FieldPanel("enrolled_count")], heading="Stats"),
        MultiFieldPanel([FieldPanel("is_published"), FieldPanel("created_at")], heading="Publishing"),
    ]

    search_fields = [
        index.SearchField("title", boost=10),
        index.SearchField("description", boost=5),
        index.FilterField("is_published"),
    ]

    class Meta:
        app_label = "content"
        verbose_name = _("course")
        verbose_name_plural = _("courses")
        ordering = ["-created_at"]

    def __str__(self): return self.title
