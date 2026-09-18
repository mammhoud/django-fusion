"""Generic marketing/content page for static Astro routes.

Powers the /faq/, /pricing/, /features/, /projects/ and /products/ routes.
Each route is an Astro page that renders *only* backend data (no hardcoded
fallbacks), so this model exposes the exact StreamField names the frontend
reads from /apis/pages/<slug>/:

- ``faq``      → [{question, answer}]
- ``pricing``  → [{tiers: [{name, price, period, description, features,
                  featured, cta_label, cta_href}]}]
- ``features`` → [{title, description, icon}]
- ``projects`` → [{name, edition, category, path, description,
                  features: [{label, shared}]}]
- ``products`` → [{title, slug, tagline, href}]
- ``stats``    → [{label, value, suffix}]
- ``CTA``      → [{title, subtitle, primary_cta: {label, href}}]

All fields are Wagtail-editable and localized per locale via the standard
translation workflow (translation_key chain, see LEARNING_CASES Case 8).
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from .base import BasePage


class FaqItemBlock(blocks.StructBlock):
    question = blocks.CharBlock(max_length=300, label=_("Question"))
    answer = blocks.TextBlock(label=_("Answer"))

    class Meta:
        icon = "help"
        label = _("FAQ Item")


class PricingTierBlock(blocks.StructBlock):
    name = blocks.CharBlock(max_length=100, label=_("Plan Name"))
    price = blocks.CharBlock(max_length=20, default="0", label=_("Price"))
    period = blocks.CharBlock(max_length=50, default="", label=_("Period"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    features = blocks.ListBlock(blocks.CharBlock(max_length=200), label=_("Features"))
    featured = blocks.BooleanBlock(default=False, required=False, label=_("Highlighted"))
    cta_label = blocks.CharBlock(max_length=50, default="Get started", label=_("CTA Label"))
    cta_href = blocks.CharBlock(max_length=300, default="/#cta", label=_("CTA Link"))

    class Meta:
        icon = "list-ul"
        label = _("Pricing Tier")


class PricingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=200, required=False, label=_("Heading"))
    intro = blocks.TextBlock(required=False, label=_("Intro"))
    tiers = blocks.ListBlock(PricingTierBlock(), label=_("Tiers"))

    class Meta:
        icon = "table"
        label = _("Pricing")


class FeatureBlock(blocks.StructBlock):
    icon = blocks.CharBlock(max_length=200, required=False, label=_("Icon (SVG path or class)"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(label=_("Description"))

    class Meta:
        icon = "cog"
        label = _("Feature")


class ProjectFeatureBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=200, label=_("Label"))
    shared = blocks.BooleanBlock(default=True, required=False, label=_("Shared"))

    class Meta:
        icon = "check"
        label = _("Project Feature")


class ProjectBlock(blocks.StructBlock):
    name = blocks.CharBlock(max_length=200, label=_("Name"))
    edition = blocks.CharBlock(max_length=100, required=False, label=_("Edition"))
    category = blocks.CharBlock(max_length=100, default="program", label=_("Category"))
    path = blocks.CharBlock(max_length=200, required=False, label=_("Path"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    features = blocks.ListBlock(ProjectFeatureBlock(), required=False, label=_("Features"))

    class Meta:
        icon = "folder-open-inverse"
        label = _("Project")


class ProductBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    slug = blocks.CharBlock(max_length=200, required=False, label=_("Slug"))
    tagline = blocks.TextBlock(required=False, label=_("Tagline"))
    href = blocks.CharBlock(max_length=300, default="/services/", label=_("Link"))

    class Meta:
        icon = "doc-full"
        label = _("Product")


class StatBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=100, label=_("Label"))
    value = blocks.CharBlock(max_length=50, label=_("Value"))
    suffix = blocks.CharBlock(max_length=20, default="", required=False, label=_("Suffix"))

    class Meta:
        icon = "order"
        label = _("Stat")


class CtaContentBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    subtitle = blocks.TextBlock(required=False, label=_("Subtitle"))
    primary_cta = blocks.StructBlock(
        [
            ("label", blocks.CharBlock(max_length=50, default="Get in touch", label=_("Label"))),
            ("href", blocks.CharBlock(max_length=300, default="/contact/", label=_("Link"))),
        ],
        label=_("Primary CTA"),
    )

    class Meta:
        icon = "success"
        label = _("CTA Content")


class MarketingPage(BasePage):
    """Wagtail content source for the static marketing routes."""

    template = "base_page.html"
    template_name = "pages/page.html"
    fragment_name = "pages.page"
    page_title = _("Marketing Page")

    hero_heading = models.CharField(max_length=200, blank=True, default="", verbose_name=_("Hero Heading"))
    hero_subheading = models.TextField(blank=True, default="", verbose_name=_("Hero Subheading"))
    intro_text = models.TextField(blank=True, default="", verbose_name=_("Intro Text"))

    faq = StreamField(
        [("faq_item", FaqItemBlock())],
        use_json_field=True, null=True, blank=True,
        verbose_name=_("FAQ"),
    )
    pricing = StreamField(
        [("pricing", PricingBlock())],
        use_json_field=True, null=True, blank=True,
        verbose_name=_("Pricing"),
    )
    features = StreamField(
        [("feature", FeatureBlock())],
        use_json_field=True, null=True, blank=True,
        verbose_name=_("Features"),
    )
    projects = StreamField(
        [("project", ProjectBlock())],
        use_json_field=True, null=True, blank=True,
        verbose_name=_("Projects"),
    )
    products = StreamField(
        [("product", ProductBlock())],
        use_json_field=True, null=True, blank=True,
        verbose_name=_("Products"),
    )
    stats = StreamField(
        [("stat", StatBlock())],
        use_json_field=True, null=True, blank=True,
        verbose_name=_("Stats"),
    )
    CTA = StreamField(
        [("cta_content", CtaContentBlock())],
        use_json_field=True, null=True, blank=True,
        verbose_name=_("CTA Section"),
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("hero_heading"), FieldPanel("hero_subheading"), FieldPanel("intro_text")],
            heading=_("Hero"),
        ),
        FieldPanel("faq"),
        FieldPanel("pricing"),
        FieldPanel("features"),
        FieldPanel("projects"),
        FieldPanel("products"),
        FieldPanel("stats"),
        FieldPanel("CTA"),
    ]

    subpage_types = []

    class Meta:
        db_table = "content_marketingpage"
        verbose_name = _("marketing page")
        verbose_name_plural = _("marketing pages")
