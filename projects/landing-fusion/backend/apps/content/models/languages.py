"""
Site languages — the seeded, admin-editable language catalog.

Every language the site offers (UI chrome + editorial content) is a row in
this snippet. The seed command populates it from ``DEFAULT_SITE_LANGUAGES``
(mirroring the Astro ``LANG_META`` table), editors can reorder/disable
entries from the Wagtail admin, and ``GET /apis/content/languages/`` serves
the active rows to the frontend switcher.

Editorial content itself stays in the ``PageTranslation`` snippet (seeded
overlays for every catalog language, English canonical), while this catalog
governs which languages the switcher can offer.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


# Keep the learner catalog aligned with the site switcher. Editorial overlays
# cover every catalog language (English canonical; untranslated fields fall
# back through the PageTranslation merge contract).
SUPPORTED_LANGUAGE_CHOICES = (
    ("en", _("English")),
    ("ar", _("Arabic")),
    ("sv", _("Swedish")),
    ("fr", _("French")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("pt", _("Portuguese")),
)
SUPPORTED_LANGUAGE_CODES = tuple(code for code, _ in SUPPORTED_LANGUAGE_CHOICES)


@register_snippet
class SiteLanguage(models.Model):
    """One supported language offered in the site language switcher."""

    code = models.CharField(
        max_length=10,
        choices=SUPPORTED_LANGUAGE_CHOICES,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("BCP-47 language tag, for example en, ar, sv."),
    )
    name = models.CharField(
        max_length=60,
        verbose_name=_("Name"),
        help_text=_("English display name, for example English, Arabic."),
    )
    native_name = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name=_("Native name"),
        help_text=_("Name in the language itself, for example Svenska, العربية."),
    )
    direction = models.CharField(
        max_length=3,
        choices=[("ltr", _("Left to right")), ("rtl", _("Right to left"))],
        default="ltr",
        verbose_name=_("Direction"),
    )
    flag = models.CharField(
        max_length=8,
        blank=True,
        default="",
        verbose_name=_("Flag emoji"),
        help_text=_("Emoji flag shown in the switcher, for example 🇸🇪."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Active"),
        help_text=_("Inactive languages are hidden from the switcher."),
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name=_("Sort order"),
        help_text=_("Lower numbers appear first in the switcher."),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("code"),
                FieldPanel("name"),
                FieldPanel("native_name"),
                FieldPanel("direction"),
                FieldPanel("flag"),
            ],
            heading=_("Language identity"),
        ),
        MultiFieldPanel(
            [FieldPanel("is_active"), FieldPanel("sort_order")],
            heading=_("Visibility"),
        ),
    ]

    class Meta:
        app_label = "content"
        ordering = ["sort_order", "code"]
        verbose_name = _("site language")
        verbose_name_plural = _("site languages")

    def __str__(self):
        return f"{self.get_direction_display()} {self.code} ({self.name})"

    def as_dict(self) -> dict:
        """Frontend-consumable shape (mirrors the Astro ``ContentLanguage``)."""
        return {
            "code": self.code,
            "name": self.name,
            "native": self.native_name or self.name,
            "dir": self.direction,
            "flag": self.flag or "",
        }

    @classmethod
    def active(cls):
        """Active languages ordered for the switcher."""
        return cls.objects.filter(is_active=True)
