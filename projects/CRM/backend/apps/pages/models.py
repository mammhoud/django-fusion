"""Loop-CRM Wagtail landing page models.

Mirrors the precis-landing pattern: an abstract ``LandingPage`` base carrying
the shared hero + CTA sections, plus one page type per public landing URL.
Wagtail never serves public HTML — the Astro frontend owns every public route
and consumes these pages through ``/apis/pages/<slug>/``. The Wagtail admin
(/cms/) and the backend page templates exist for editors and previews.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fusion.builder.models import BuilderPage as FusionBuilderPage
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from apps.content.blocks import (
    CtaBlock,
    DnaBandBlock,
    FaqSectionBlock,
    FeaturesSectionBlock,
    HeroBlock,
    PricingSectionBlock,
    StatsSectionBlock,
    StepsSectionBlock,
)

SECTION_PANEL_CLASS = "collapsible"


class LandingPage(Page):
    """Abstract base for all landing pages — shared hero + CTA sections."""

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
    """The landing homepage — hero, DNA band, modules, steps, stats, pricing, faq, CTA."""

    dna = StreamField(
        [("dna", DnaBandBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("DNA band"),
    )
    features = StreamField(
        [("features", FeaturesSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Modules"),
    )
    steps = StreamField(
        [("steps", StepsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("How it works"),
    )
    stats = StreamField(
        [("stats", StatsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Stats"),
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
        FieldPanel("dna", classname=SECTION_PANEL_CLASS),
        FieldPanel("features", classname=SECTION_PANEL_CLASS),
        FieldPanel("steps", classname=SECTION_PANEL_CLASS),
        FieldPanel("stats", classname=SECTION_PANEL_CLASS),
        FieldPanel("pricing", classname=SECTION_PANEL_CLASS),
        FieldPanel("faq", classname=SECTION_PANEL_CLASS),
    ]

    template = "pages/home.html"
    max_count = 1
    parent_page_types = []
    subpage_types = ["pages.PricingPage", "pages.FaqPage", "pages.PrivacyPage", "pages.TermsPage"]

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")


class PricingPage(LandingPage):
    """Dedicated pricing page — editorial copy plus the tier section."""

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
        FieldPanel("pricing", classname=SECTION_PANEL_CLASS),
        FieldPanel("faq", classname=SECTION_PANEL_CLASS),
    ]

    template = "pages/pricing.html"
    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Pricing page")
        verbose_name_plural = _("Pricing pages")


class FaqPage(LandingPage):
    """Dedicated FAQ page — accordion items."""

    faq = StreamField(
        [("faq", FaqSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("FAQ"),
    )

    content_panels = LandingPage.content_panels + [
        FieldPanel("faq", classname=SECTION_PANEL_CLASS),
    ]

    template = "pages/faq.html"
    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("FAQ page")
        verbose_name_plural = _("FAQ pages")


class LegalPage(LandingPage):
    """Abstract legal page — free-form rich body for policies."""

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Policy content — paragraphs, headings, lists."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
    ]

    class Meta:
        abstract = True


class PrivacyPage(LegalPage):
    """Privacy notice page."""

    template = "pages/privacy.html"
    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Privacy page")
        verbose_name_plural = _("Privacy pages")


class TermsPage(LegalPage):
    """Terms of use page."""

    template = "pages/terms.html"
    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Terms page")
        verbose_name_plural = _("Terms pages")


class BuilderPage(FusionBuilderPage):
    """Loop-CRM landing-builder page — theme picker + dynamic sections.

    The reference consumer of the shared landing builder: editors compose a
    page from the generic fu-* section blocks, pick a theme/brand/dark mode,
    and use ``{{ variable }}`` dynamic template fields backed by
    ``template_context``. Rendered server-side for previews and exposed as
    JSON at ``/apis/builder/<slug>/`` for the Astro frontend.
    """

    template = "builder/page.html"
    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Builder page")
        verbose_name_plural = _("Builder pages")
