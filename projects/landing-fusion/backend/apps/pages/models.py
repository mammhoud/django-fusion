"""
Landing-fusion Wagtail page models.

Each page type carries the editable fields that drive the Astro frontend
sections (hero, stats, features, testimonials, pricing, faq, cta, contact).
Mirrors the structure of ``cms-fusion/backend/apps/content/models/pages/`` but
trimmed to the landing slice — see plan §5.1 / §5.3.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from apps.content.blocks import (
    ContactSectionBlock,
    CtaBlock,
    FaqSectionBlock,
    FeaturesSectionBlock,
    HeroBlock,
    PricingSectionBlock,
    ProjectBlock,
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


class SectionStackMixin(models.Model):
    """
    The full landing section stack (stats, features, testimonials, pricing, faq).

    Carried by ``AboutPage`` — the single page that renders the whole document.
    ``HomePage`` stays slim (hero + CTA only), mirroring the Astro frontend
    where /about is the full story and / is a one-screen entry point.
    """

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

    class Meta:
        abstract = True

    section_panels = [
        FieldPanel("stats", classname=SECTION_PANEL_CLASS),
        FieldPanel("features", classname=SECTION_PANEL_CLASS),
        FieldPanel("testimonials", classname=SECTION_PANEL_CLASS),
        FieldPanel("pricing", classname=SECTION_PANEL_CLASS),
        FieldPanel("faq", classname=SECTION_PANEL_CLASS),
    ]


class HomePage(LandingPage):
    """
    Landing homepage — a slim one-screen entry (hero + CTA).

    The full document (stats, features, testimonials, pricing, faq) lives on
    the About page; this page exists to hand visitors over to it.
    """

    template = "pages/home.html"
    max_count = 1

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")


class AboutPage(SectionStackMixin, LandingPage):
    """About page — the full document: hero, mission, stats, features, pricing, testimonials, faq, cta."""

    # Heading used by the shared content-region partial (pages/partials/page_content.html).
    body_heading = _("Our mission")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Mission, story and values content."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Mission"),
            classname=SECTION_PANEL_CLASS,
        ),
        *SectionStackMixin.section_panels,
    ]

    template = "pages/about.html"

    class Meta:
        verbose_name = _("About page")
        verbose_name_plural = _("About pages")


class CompanyPage(LandingPage):
    """Company page — hero, story, values."""

    body_heading = _("Who we are")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Company story, mission and values content."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
    ]

    template = "pages/company.html"

    class Meta:
        verbose_name = _("Company page")
        verbose_name_plural = _("Company pages")


class ServicesPage(LandingPage):
    """Services page — hero, offering, approach."""

    body_heading = _("What we do")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Services, offering and approach content."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
    ]

    template = "pages/services.html"

    class Meta:
        verbose_name = _("Services page")
        verbose_name_plural = _("Services pages")


class ProductsPage(SectionStackMixin, LandingPage):
    """Products page — the full product document: hero, lines, stats, features, pricing, testimonials, faq, cta."""

    body_heading = _("What ships with Fusion")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Product lines and highlights content."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
        *SectionStackMixin.section_panels,
    ]

    template = "pages/products.html"

    class Meta:
        verbose_name = _("Products page")
        verbose_name_plural = _("Products pages")


class FeaturesPage(SectionStackMixin, LandingPage):
    """Features page — the full capability document: hero, stack, stats, features, pricing, testimonials, faq, cta."""

    body_heading = _("The stack, explained")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Capability and stack content."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
        *SectionStackMixin.section_panels,
    ]

    template = "pages/features.html"

    class Meta:
        verbose_name = _("Features page")
        verbose_name_plural = _("Features pages")


class ProjectsPage(SectionStackMixin, LandingPage):
    """
    Projects page — the full project document: hero, body, the repo's project cards
    (with editions and shared/standalone features), then the shared section stack.
    """

    body_heading = _("Built from this monorepo")
    projects_heading = _("Projects in this repo")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Intro text above the project cards."),
    )
    projects = StreamField(
        [("project", ProjectBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Projects"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("projects"),
        *SectionStackMixin.section_panels,
    ]

    template = "pages/projects.html"

    class Meta:
        verbose_name = _("Projects page")
        verbose_name_plural = _("Projects pages")


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

    template = "pages/contact.html"

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

    template = "pages/faq.html"

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

    template = "pages/privacy.html"

    class Meta:
        verbose_name = _("Privacy page")
        verbose_name_plural = _("Privacy pages")
