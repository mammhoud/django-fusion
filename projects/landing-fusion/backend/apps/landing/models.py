"""
Landing-fusion Wagtail page models.

Each page type carries the editable fields that drive the Astro frontend
sections (hero, stats, features, testimonials, pricing, faq, cta, contact).
Mirrors the structure of ``cms-fusion/backend/apps/content/models/pages/`` but
trimmed to the landing slice — see plan §5.1 / §5.3.
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from .blocks import (
    ContactSectionBlock,
    CtaBlock,
    FaqSectionBlock,
    FeaturesSectionBlock,
    HeroBlock,
    PricingSectionBlock,
    StatsSectionBlock,
    TestimonialsSectionBlock,
)

SECTION_PANEL_CLASS = "collapsible"


class LandingPage(Page):
    """
    Abstract base for all landing pages.

    Provides the shared hero + CTA sections plus SEO-friendly search fields,
    mirroring ``BasePage`` in the CMS-Fusion backend but without the
    django-fusion routing machinery (the Astro frontend handles rendering).
    """

    hero = StreamField(
        [("hero", HeroBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Hero"),
    )
    cta = StreamField(
        [("cta", CtaBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Call to action"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("hero"),
        FieldPanel("cta"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("hero"),
    ]

    class Meta:
        abstract = True


class HomePage(LandingPage):
    """Landing homepage — the full section stack."""

    stats = StreamField(
        [("stats", StatsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Stats"),
    )
    features = StreamField(
        [("features", FeaturesSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Features"),
    )
    testimonials = StreamField(
        [("testimonials", TestimonialsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Testimonials"),
    )
    pricing = StreamField(
        [("pricing", PricingSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Pricing"),
    )
    faq = StreamField(
        [("faq", FaqSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("FAQ"),
    )

    content_panels = LandingPage.content_panels + [
        FieldPanel("stats", classname=SECTION_PANEL_CLASS),
        FieldPanel("features", classname=SECTION_PANEL_CLASS),
        FieldPanel("testimonials", classname=SECTION_PANEL_CLASS),
        FieldPanel("pricing", classname=SECTION_PANEL_CLASS),
        FieldPanel("faq", classname=SECTION_PANEL_CLASS),
    ]

    template = "landing/home.html"
    max_count = 1

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")


class AboutPage(LandingPage):
    """About page — hero, mission, values."""

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Mission, story and values content."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
    ]

    template = "landing/about.html"

    class Meta:
        verbose_name = _("About page")
        verbose_name_plural = _("About pages")


class ContactPage(LandingPage):
    """Contact page — info cards + form section."""

    contact = StreamField(
        [("contact", ContactSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Contact section"),
    )

    content_panels = LandingPage.content_panels + [
        FieldPanel("contact"),
    ]

    template = "landing/contact.html"

    class Meta:
        verbose_name = _("Contact page")
        verbose_name_plural = _("Contact pages")


class FaqPage(LandingPage):
    """Dedicated FAQ page."""

    faq = StreamField(
        [("faq", FaqSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("FAQ"),
    )

    content_panels = LandingPage.content_panels + [
        FieldPanel("faq"),
    ]

    template = "landing/faq.html"

    class Meta:
        verbose_name = _("FAQ page")
        verbose_name_plural = _("FAQ pages")


class PrivacyPage(LandingPage):
    """Privacy policy page — static rich content."""

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
    ]

    template = "landing/privacy.html"

    class Meta:
        verbose_name = _("Privacy page")
        verbose_name_plural = _("Privacy pages")
