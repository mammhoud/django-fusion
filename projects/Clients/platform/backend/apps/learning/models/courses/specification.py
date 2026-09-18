from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable

from .detail import Module


class Lesson(Orderable, ClusterableModel):
    module = ParentalKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = RichTextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("content"),
        FieldPanel("duration_minutes"),
        FieldPanel("is_preview"),
        FieldPanel("is_active"),
        FieldPanel("order"),
        InlinePanel("resources", heading=_("Lesson Resources"), label=_("Resource")),
    ]

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["module", "order"], name="learning_lesson_order")
        ]

    def __str__(self):
        return self.title


class LessonResource(Orderable):
    """Downloadable resource attached to a lesson (Precis parity)."""

    lesson = ParentalKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="resources",
        verbose_name=_("Parent Lesson"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Resource title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    file = models.FileField(upload_to="lesson_resources/", verbose_name=_("File"))
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ("slides", _("Slides")),
            ("code", _("Code files")),
            ("document", _("Document")),
            ("exercise", _("Exercise")),
            ("other", _("Other")),
        ],
        default="document",
        verbose_name=_("Resource type"),
    )
    is_free = models.BooleanField(
        default=False,
        verbose_name=_("Free resource"),
        help_text=_("Available without enrollment"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("file"),
        FieldPanel("resource_type"),
        FieldPanel("is_free"),
    ]

    class Meta:
        verbose_name = _("Lesson resource")
        verbose_name_plural = _("Lesson resources")

    def __str__(self):
        return f"{self.title} — {self.lesson.title}"
