"""Locale overlays for events (the EventTranslation contract).

The events calendar keeps one canonical Event row per event.  These records
add a small, editor-managed translation layer for the Astro/data-API road —
mirroring the landing ``PageTranslation`` and learning ``CourseTranslation``
snippets — without a second event tree or an external translation package.

Overlay fields are intentionally partial: empty fields keep falling back to
the canonical English content through the API merge contract.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from apps.content.models.languages import SUPPORTED_LANGUAGE_CHOICES


class EventTranslation(models.Model):
    """A locale-specific editorial overlay for one published event.

    ``title``, ``description`` and ``location`` override the canonical English
    event fields.  The requested locale is resolved by the API when ``?lang=``
    is present; anything left empty falls back to the canonical row.
    """

    event = models.ForeignKey(
        "handlers.Event",
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name=_("Event"),
    )
    language = models.CharField(
        max_length=10,
        choices=SUPPORTED_LANGUAGE_CHOICES,
        verbose_name=_("Language"),
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Translated event title. Empty uses the canonical title."),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Translated event description. Empty uses the canonical description."),
    )
    location = models.CharField(
        max_length=250,
        blank=True,
        help_text=_("Translated venue or meeting location. Empty uses the canonical location."),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_id", "language"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "language"],
                name="unique_handlers_event_translation",
            )
        ]
        verbose_name = _("Event translation")
        verbose_name_plural = _("Event translations")

    panels = [
        MultiFieldPanel(
            [FieldPanel("event"), FieldPanel("language")],
            heading=_("Translation identity"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("description"),
                FieldPanel("location"),
            ],
            heading=_("Event content"),
        ),
    ]

    def __str__(self):
        return f"{self.event.title} ({self.language})"

    @classmethod
    def for_event(cls, event, language: str):
        """Resolve one requested translation from the supported catalog."""
        if language not in dict(SUPPORTED_LANGUAGE_CHOICES):
            return None
        return cls.objects.filter(event=event, language=language).first()
