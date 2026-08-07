"""Editorial English/Arabic translations for landing Wagtail pages.

The landing site keeps the canonical page tree in Wagtail.  These records add
an intentionally small translation layer for the Astro/data-API road without
requiring a second page tree or an external translation package.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


CONTENT_LANGUAGE_CHOICES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
]


@register_snippet
class PageTranslation(models.Model):
    """A locale-specific editorial overlay for one published Wagtail page.

    ``content`` stores top-level API keys such as ``hero``, ``cta`` or
    ``features``.  The page API deep-merges those keys over the canonical
    English serialization, so a partial Arabic translation can safely fall
    back to the base content while editors translate it incrementally.
    """

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="landing_translations",
        verbose_name=_("Page"),
    )
    language = models.CharField(
        max_length=2,
        choices=CONTENT_LANGUAGE_CHOICES,
        verbose_name=_("Language"),
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Translated page title. Empty uses the canonical page title."),
    )
    search_description = models.TextField(
        blank=True,
        help_text=_("Translated SEO description."),
    )
    body = models.TextField(
        blank=True,
        help_text=_("Translated rich-text HTML. Empty uses the canonical body."),
    )
    content = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Partial API content overrides, for example hero, cta, faq, or features."),
    )
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel(
            [FieldPanel("page"), FieldPanel("language")],
            heading=_("Translation identity"),
        ),
        MultiFieldPanel(
            [FieldPanel("title"), FieldPanel("search_description"), FieldPanel("body")],
            heading=_("SEO and body"),
        ),
        FieldPanel("content"),
    ]

    class Meta:
        ordering = ["page_id", "language"]
        constraints = [
            models.UniqueConstraint(
                fields=["page", "language"],
                name="unique_landing_page_translation",
            )
        ]
        verbose_name = _("page translation")
        verbose_name_plural = _("page translations")

    def __str__(self):
        return f"{self.page.title} ({self.language})"

    def as_overrides(self) -> dict:
        """Return only non-empty scalar fields plus valid JSON content."""
        raw_content = self.content if isinstance(self.content, dict) else {}
        overrides = dict(raw_content)
        if self.title:
            overrides["title"] = self.title
        if self.search_description:
            overrides["search_description"] = self.search_description
        if self.body:
            overrides["body"] = self.body
        return overrides

    @classmethod
    def for_page(cls, page, language: str) -> "PageTranslation | None":
        """Resolve one requested translation, restricting to en/ar."""
        if language not in dict(CONTENT_LANGUAGE_CHOICES):
            return None
        return cls.objects.filter(page=page, language=language).first()
