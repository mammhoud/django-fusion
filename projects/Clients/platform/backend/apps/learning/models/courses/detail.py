from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable

from .info import Course


class Module(Orderable, ClusterableModel):
    course = ParentalKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("order"),
        InlinePanel("lessons", label=_("Lesson")),
    ]

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="learning_module_order")
        ]

    def __str__(self):
        return self.title

    @property
    def lessons_count(self):
        """Number of lessons in this module (mirrors Precis naming)."""
        return self.lessons.count()


class Specialization(models.Model):
    """Specialization/subject area a course can belong to (Precis parity)."""

    title = models.CharField(max_length=200, verbose_name=_("Specialization title"))
    slug = models.SlugField(unique=True, max_length=200, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display order"))

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        verbose_name = _("Specialization")
        verbose_name_plural = _("Specializations")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
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
        return self.courses.filter(is_published=True).count()
