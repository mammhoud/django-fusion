"""Locale overlays for learning courses (the CourseTranslation contract).

The course catalog keeps one canonical Course row per course.  These records
add a small, editor-managed translation layer for the Astro/data-API road —
mirroring the landing ``PageTranslation`` snippet — without a second course
tree or an external translation package.

Overlay fields are intentionally partial: empty fields keep falling back to
the canonical English content through the API merge contract.  The ``content``
JSON field carries module/lesson title overrides keyed by ``order``, so a
partial translation can localize the module tree without duplicating every
lesson record.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from apps.content.models.languages import SUPPORTED_LANGUAGE_CHOICES
from apps.content.models.translations import CONTENT_LANGUAGE_CHOICES


# Registered as a Wagtail snippet via ``CourseTranslationSnippetViewSet`` in
# ``apps.learning.wagtail_hooks`` (the model keeps its panels beside the content).
class CourseTranslation(models.Model):
    """A locale-specific editorial overlay for one published course.

    ``title``, ``short_description``, ``description``, ``objectives``,
    ``requirements`` and ``target_audience`` override the canonical English
    course fields.  ``content`` holds module/lesson overrides keyed by order:

        {"modules": {"1": {"title": "...", "description": "...",
                           "lessons": {"0": {"title": "..."}}}}}
    """

    course = models.ForeignKey(
        "learning.Course",
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name=_("Course"),
    )
    language = models.CharField(
        max_length=10,
        choices=CONTENT_LANGUAGE_CHOICES,
        verbose_name=_("Language"),
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Translated course title. Empty uses the canonical title."),
    )
    short_description = models.TextField(
        blank=True,
        help_text=_("Translated catalog short description."),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Translated rich-text HTML description. Empty uses the canonical body."),
    )
    objectives = models.TextField(
        blank=True,
        help_text=_("Translated learning objectives — one per line."),
    )
    requirements = models.TextField(
        blank=True,
        help_text=_("Translated prerequisites — one per line."),
    )
    target_audience = models.TextField(
        blank=True,
        help_text=_("Translated target audience — one per line."),
    )
    content = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Partial module/lesson overrides keyed by order."),
    )
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel(
            [FieldPanel("course"), FieldPanel("language")],
            heading=_("Translation identity"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("short_description"),
                FieldPanel("description"),
            ],
            heading=_("Course content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("objectives"),
                FieldPanel("requirements"),
                FieldPanel("target_audience"),
            ],
            heading=_("Learning metadata"),
        ),
        FieldPanel("content"),
    ]

    class Meta:
        ordering = ["course_id", "language"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "language"],
                name="unique_learning_course_translation",
            )
        ]
        verbose_name = _("Course translation")
        verbose_name_plural = _("Course translations")

    def __str__(self):
        return f"{self.course.title} ({self.language})"

    @classmethod
    def for_course(cls, course, language: str):
        """Resolve one requested translation from the supported catalog."""
        if language not in dict(SUPPORTED_LANGUAGE_CHOICES):
            return None
        return cls.objects.filter(course=course, language=language).first()
