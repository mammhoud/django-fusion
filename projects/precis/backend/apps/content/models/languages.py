"""Admin-editable language catalog for the Precis Fusion site."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


SUPPORTED_LANGUAGE_CHOICES = (
    ("en", _("English")),
    ("sv", _("Swedish")),
    ("fr", _("French")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("ar", _("Arabic")),
    ("pt-br", _("Portuguese (Brazil)")),
)
SUPPORTED_LANGUAGE_CODES = tuple(code for code, _ in SUPPORTED_LANGUAGE_CHOICES)


@register_snippet
class SiteLanguage(models.Model):
    """One language offered by the site and its editorial API."""

    code = models.CharField(max_length=10, choices=SUPPORTED_LANGUAGE_CHOICES, unique=True)
    name = models.CharField(max_length=60)
    native_name = models.CharField(max_length=60, blank=True, default="")
    direction = models.CharField(
        max_length=3,
        choices=(("ltr", _("Left to right")), ("rtl", _("Right to left"))),
        default="ltr",
    )
    flag = models.CharField(max_length=8, blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    panels = [
        MultiFieldPanel(
            [FieldPanel("code"), FieldPanel("name"), FieldPanel("native_name"),
             FieldPanel("direction"), FieldPanel("flag")],
            heading=_("Language identity"),
        ),
        MultiFieldPanel(
            [FieldPanel("is_active"), FieldPanel("sort_order")],
            heading=_("Visibility"),
        ),
    ]

    class Meta:
        ordering = ["sort_order", "code"]
        verbose_name = _("site language")
        verbose_name_plural = _("site languages")

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def as_dict(self) -> dict[str, str | int | bool]:
        return {
            "code": self.code,
            "name": self.name,
            "native": self.native_name or self.name,
            "dir": self.direction,
            "flag": self.flag,
            "active": self.is_active,
        }

    @classmethod
    def active(cls):
        return cls.objects.filter(is_active=True)
