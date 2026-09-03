"""
django_fusion.builder.blocks
============================

Generic, theme-agnostic Wagtail StreamField section blocks for the landing
builder.

Every text field may contain dynamic template fields (``{{ company.name }}``)
that the ``BuilderRenderer`` resolves against the page's ``template_context``
before rendering. Blocks carry no theme-specific styling — the section
templates compose the shared ``fu-*`` component classes, so a page re-skins
instantly when its ``theme`` field changes.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class LinkBlock(blocks.StructBlock):
    """A link with a label — an internal page chooser wins over a manual URL."""

    label = blocks.CharBlock(max_length=80, label=_("Label"))
    href = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_("URL"),
        help_text=_("External URL (e.g. https://…). Ignored when a page is chosen."),
    )
    page = blocks.PageChooserBlock(
        required=False,
        label=_("Link to a page"),
        help_text=_("Pick an internal page — its URL wins over the manual URL field."),
    )

    class Meta:
        icon = "link"
        label = _("Link")


class ButtonBlock(blocks.StructBlock):
    """CTA button in one of the shared fu-btn styles."""

    label = blocks.CharBlock(
        max_length=80,
        required=False,
        label=_("Label"),
        help_text=_("Leave empty to use the linked page's title."),
    )
    href = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_("URL"),
        help_text=_("External URL (e.g. https://…). Ignored when a page is chosen."),
    )
    page = blocks.PageChooserBlock(
        required=False,
        label=_("Link to a page"),
        help_text=_("Pick an internal page — its URL wins over the manual URL field."),
    )
    style = blocks.ChoiceBlock(
        choices=[
            ("primary", _("Primary")),
            ("secondary", _("Secondary")),
            ("outline", _("Outline")),
            ("ghost", _("Ghost")),
        ],
        default="primary",
        label=_("Style"),
    )

    class Meta:
        icon = "placeholder"
        label = _("Button")


class HeroBlock(blocks.StructBlock):
    """Landing hero — eyebrow, title + accent, lede, CTAs, footnote."""

    badge = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    accent = blocks.CharBlock(
        max_length=60,
        required=False,
        label=_("Accent word"),
        help_text=_("The emphasized word rendered in the primary color."),
    )
    subtitle = blocks.TextBlock(required=False, label=_("Subtitle / lede"))
    primary_cta = ButtonBlock(required=False, label=_("Primary CTA"))
    secondary_cta = ButtonBlock(required=False, label=_("Secondary CTA"))
    note = blocks.CharBlock(
        max_length=200,
        required=False,
        label=_("Footnote"),
        help_text=_("Small line under the CTAs."),
    )

    class Meta:
        icon = "home"
        label = _("Hero")


class FeatureBlock(blocks.StructBlock):
    """A single feature card (icon key + kicker + title + description + link)."""

    icon = blocks.CharBlock(
        max_length=80,
        required=False,
        label=_("Icon"),
        help_text=_("Optional icon key rendered by the consuming product."),
    )
    label = blocks.CharBlock(max_length=80, required=False, label=_("Kicker"))
    title = blocks.CharBlock(max_length=120, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    href = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_("URL"),
        help_text=_("Ignored when a page is chosen."),
    )
    page = blocks.PageChooserBlock(
        required=False,
        label=_("Link to a page"),
        help_text=_("Pick an internal page instead of typing a URL."),
    )

    class Meta:
        icon = "placeholder"
        label = _("Feature card")


class FeaturesSectionBlock(blocks.StructBlock):
    """Features grid with a section heading."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    features = blocks.ListBlock(FeatureBlock(), label=_("Features"))

    class Meta:
        icon = "list-ul"
        label = _("Features section")


class StepBlock(blocks.StructBlock):
    """One numbered step in a 'how it works' band."""

    number = blocks.CharBlock(max_length=10, label=_("Number"))
    title = blocks.CharBlock(max_length=120, label=_("Title"))
    copy = blocks.TextBlock(required=False, label=_("Copy"))

    class Meta:
        icon = "placeholder"
        label = _("Step")


class StepsSectionBlock(blocks.StructBlock):
    """Numbered steps with a section heading."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    steps = blocks.ListBlock(StepBlock(), label=_("Steps"))

    class Meta:
        icon = "list-ul"
        label = _("Steps section")


class StatBlock(blocks.StructBlock):
    """A single KPI stat (value + suffix + label)."""

    value = blocks.CharBlock(max_length=20, label=_("Value"))
    suffix = blocks.CharBlock(max_length=10, required=False, label=_("Suffix"))
    label = blocks.CharBlock(max_length=120, label=_("Label"))

    class Meta:
        icon = "placeholder"
        label = _("Stat")


class StatsSectionBlock(blocks.StructBlock):
    """Stats band — a row of counters."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, required=False, label=_("Section title"))
    stats = blocks.ListBlock(StatBlock(), label=_("Stats"))

    class Meta:
        icon = "doc-full"
        label = _("Stats section")


class PricingTierBlock(blocks.StructBlock):
    """A pricing tier (name, price, features, CTA, featured flag)."""

    name = blocks.CharBlock(max_length=80, label=_("Name"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    price = blocks.CharBlock(max_length=20, label=_("Price"))
    period = blocks.CharBlock(max_length=40, required=False, label=_("Period"))
    features = blocks.ListBlock(blocks.CharBlock(max_length=160), label=_("Features"))
    cta_label = blocks.CharBlock(max_length=80, required=False, label=_("CTA label"))
    cta_href = blocks.CharBlock(max_length=255, required=False, label=_("CTA URL"))
    cta_page = blocks.PageChooserBlock(
        required=False,
        label=_("CTA page"),
        help_text=_("Pick an internal page instead of typing a CTA URL."),
    )
    featured = blocks.BooleanBlock(required=False, default=False, label=_("Featured"))

    class Meta:
        icon = "placeholder"
        label = _("Pricing tier")


class PricingSectionBlock(blocks.StructBlock):
    """Pricing section with a heading and a list of tiers."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    tiers = blocks.ListBlock(PricingTierBlock(), label=_("Tiers"))

    class Meta:
        icon = "list-ul"
        label = _("Pricing section")


class FaqItemBlock(blocks.StructBlock):
    """A single FAQ accordion item."""

    question = blocks.CharBlock(max_length=200, label=_("Question"))
    answer = blocks.TextBlock(required=False, label=_("Answer"))

    class Meta:
        icon = "help"
        label = _("FAQ item")


class FaqSectionBlock(blocks.StructBlock):
    """FAQ section with a heading and accordion items."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    items = blocks.ListBlock(FaqItemBlock(), label=_("FAQ items"))

    class Meta:
        icon = "help"
        label = _("FAQ section")


class CtaBlock(blocks.StructBlock):
    """Full-width CTA banner (title + subtitle + buttons)."""

    title = blocks.CharBlock(max_length=200, label=_("Title"))
    subtitle = blocks.TextBlock(required=False, label=_("Subtitle"))
    primary_cta = ButtonBlock(required=False, label=_("Primary CTA"))
    secondary_cta = ButtonBlock(required=False, label=_("Secondary CTA"))

    class Meta:
        icon = "warning"
        label = _("CTA")


#: The section stack offered to editors, in render order.
BUILDER_SECTION_BLOCKS = [
    ("hero", HeroBlock()),
    ("features", FeaturesSectionBlock()),
    ("steps", StepsSectionBlock()),
    ("stats", StatsSectionBlock()),
    ("pricing", PricingSectionBlock()),
    ("faq", FaqSectionBlock()),
    ("cta", CtaBlock()),
]


__all__ = [
    "BUILDER_SECTION_BLOCKS",
    "ButtonBlock",
    "CtaBlock",
    "FaqItemBlock",
    "FaqSectionBlock",
    "FeatureBlock",
    "FeaturesSectionBlock",
    "HeroBlock",
    "LinkBlock",
    "PricingSectionBlock",
    "PricingTierBlock",
    "StatBlock",
    "StatsSectionBlock",
    "StepBlock",
    "StepsSectionBlock",
]
