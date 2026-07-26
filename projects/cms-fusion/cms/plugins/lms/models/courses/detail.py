import logging

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as DefaultBase
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.models import Orderable

from .info import Course

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# MODULE MODEL
# -------------------------------------------------------------------
class Module(DefaultBase, Orderable, ClusterableModel):
    """Course module grouping lessons and activities."""

    course = ParentalKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=_("Parent Course"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Module Order"))
    title = models.CharField(max_length=200, verbose_name=_("Module Title"))
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Brief description of this module"),
    )
    is_preview = models.BooleanField(
        default=False,
        verbose_name=_("Preview Module"),
        help_text=_("Make this module available for preview"),
    )
    is_extra = models.BooleanField(default=False, verbose_name=_("Is Extra Content"))
    has_quiz = models.BooleanField(default=False, verbose_name=_("Has Quiz"))
    has_assignment = models.BooleanField(
        default=False, verbose_name=_("Has Assignment")
    )
    canonical_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Canonical URL"),
        help_text=_("Optional canonical URL for SEO"),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("description"),
                FieldPanel("order"),
                FieldPanel("has_assignment"),
                FieldPanel("canonical_url"),
            ],
            heading=_("Module Configuration"),
        ),
        InlinePanel("lessons", heading=_("Lessons"), label=_("Lesson")),
    ]

    class Meta:
        app_label = "lms"
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")
        constraints = [
            models.UniqueConstraint(
                fields=["order", "course"], name="unique_order_per_course"
            )
        ]
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} ({self.course.title})"

    @property
    def duration(self):
        """Calculate total duration of all lessons in this module."""
        return sum(lesson.duration for lesson in self.lessons.all())

    @property
    def lessons_count(self):
        """Get number of lessons in this module."""
        return self.lessons.count()


# -------------------------------------------------------------------
# SPECIALIZATION MODEL (if not already defined)
# -------------------------------------------------------------------
class Specialization(DefaultBase):
    """Specialization/Subject area for courses."""

    title = models.CharField(max_length=200, verbose_name=_("Specialization Title"))
    slug = models.SlugField(unique=True, max_length=200, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="specialization_icons",
        verbose_name=_("Icon"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        app_label = "lms"
        verbose_name = _("Specialization")
        verbose_name_plural = _("Specializations")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Specialization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def course_count(self):
        """Count published courses in this specialization."""
        return self.courses.filter(is_published=True, is_active=True).count()


# -------------------------------------------------------------------
# COURSE CATEGORY MODEL
# -------------------------------------------------------------------
class CourseCategory(DefaultBase):
    """Category area for courses."""

    title = models.CharField(max_length=200, verbose_name=_("Category Title"))
    slug = models.SlugField(unique=True, max_length=200, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="category_icons",
        verbose_name=_("Icon"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        app_label = "lms"
        verbose_name = _("Course Category")
        verbose_name_plural = _("Course Categories")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while CourseCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def course_count(self):
        """Count published courses in this category."""
        return self.courses.filter(is_published=True, is_active=True).count()



