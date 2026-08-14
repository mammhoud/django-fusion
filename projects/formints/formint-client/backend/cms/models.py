"""
CMS models — Wagtail pages, blocks (badges / stars), and site settings.

The purchase-app portal owns the storefront routes (/, /menu, /orders …) while
Wagtail manages editorial pages (about, press, brand) under their own slugs.
The theme lives as Wagtail site settings so editors control the design system
tokens (mode, accent, font pair, radius, density) without touching code.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel


# ── Blocks ────────────────────────────────────────────────────────────

class BadgeBlock(blocks.StructBlock):
    """A single award/rating badge — icon or star rating with a label."""

    label = blocks.CharBlock(max_length=80, required=True, help_text=_("Badge label, e.g. “Top Rated”"))
    sublabel = blocks.CharBlock(
        max_length=120, required=False, help_text=_("Supporting line, e.g. “Google Reviews · 4.9”")
    )
    stars = blocks.IntegerBlock(
        min_value=1,
        max_value=5,
        required=False,
        help_text=_("Show a star rating (1–5) instead of the icon below."),
    )
    kind = blocks.ChoiceBlock(
        choices=[
            ("star", _("Star")),
            ("award", _("Award")),
            ("shield", _("Shield")),
            ("check", _("Check")),
            ("flame", _("Flame")),
            ("sparkle", _("Sparkle")),
        ],
        default="star",
        required=False,
    )
    tone = blocks.ChoiceBlock(
        choices=[
            ("gold", _("Gold")),
            ("primary", _("Brand (verdigris)")),
            ("success", _("Success")),
            ("warning", _("Warning")),
            ("danger", _("Danger")),
        ],
        default="gold",
        required=False,
    )

    class Meta:
        icon = "success"
        label = _("Badge")


class BadgesSectionBlock(blocks.StructBlock):
    """A row of award/rating badges with an optional heading."""

    eyebrow = blocks.CharBlock(max_length=60, required=False)
    title = blocks.CharBlock(max_length=120, required=False)
    description = blocks.TextBlock(required=False, rows=2)
    badges = blocks.ListBlock(BadgeBlock(), label=_("Badges"))

    class Meta:
        icon = "success"
        label = _("Badges section")


class HeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=120, required=True)
    level = blocks.ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3")], default="h2", required=False
    )

    class Meta:
        icon = "title"
        label = _("Heading")


class ParagraphBlock(blocks.RichTextBlock):
    class Meta:
        icon = "pilcrow"
        label = _("Paragraph")


# ── Pages ─────────────────────────────────────────────────────────────

class CmsPage(Page):
    """A simple editorial page with headings, paragraphs, and badge sections."""

    body = StreamField(
        [
            ("heading", HeadingBlock()),
            ("paragraph", ParagraphBlock()),
            ("badges", BadgesSectionBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    max_count = 50

    template = "cms/cms_page.html"

    class Meta:
        verbose_name = _("CMS page")


# ── Site settings (theme as Wagtail settings) ─────────────────────────

@register_setting
class ThemeSettings(BaseSiteSetting):
    """Design-system tokens configurable from the Wagtail admin."""

    mode = models.CharField(
        max_length=10,
        choices=[("light", _("Light")), ("dark", _("Dark")), ("system", _("System"))],
        default="light",
        help_text=_("Color-scheme mode served to browsers."),
    )
    accent = models.CharField(
        max_length=7,
        default="158 42% 32%",
        help_text=_("HSL accent triple (h s% l%) — the verdigris brand token."),
    )
    font_pair = models.CharField(
        max_length=40,
        choices=[
            ("brutalist", _("Bricolage Grotesque + Public Sans")),
            ("editorial", _("Spectral + Public Sans")),
            ("mono", _("JetBrains Mono + Public Sans")),
        ],
        default="brutalist",
        help_text=_("Display/body font pairing for server-rendered pages."),
    )
    radius = models.CharField(
        max_length=10,
        choices=[
            ("sharp", _("Sharp (0.375rem)")),
            ("round", _("Round (1.25rem)")),
            ("pill", _("Pill (999px)")),
        ],
        default="round",
        help_text=_("Corner radius treatment for cards and buttons."),
    )
    density = models.CharField(
        max_length=14,
        choices=[
            ("airy", _("Airy")),
            ("comfortable", _("Comfortable")),
            ("compact", _("Compact")),
        ],
        default="comfortable",
        help_text=_("Vertical rhythm between sections."),
    )
    reduced_motion_default = models.BooleanField(
        default=False,
        help_text=_("Serve the reduced-motion stylesheet to all visitors by default."),
    )

    class Meta:
        verbose_name = _("Theme settings")
