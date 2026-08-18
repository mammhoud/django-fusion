"""Loop-CRM Wagtail StreamField blocks — the public landing section stack.

Ports the precis-landing block shapes (Hero, CTA, Features, Steps, Stats,
Pricing, FAQ, Button/Link with page-chooser resolution) trimmed to the
Loop-CRM landing sections and rendered by the Astro frontend from the
``/apis/pages/<slug>/`` JSON road. Blocks are deliberately copy-only: the
``loop-*`` BEM classes and CRT design tokens live in the Astro frontend and
the backend preview templates.
"""
from django.utils.translation import gettext_lazy as _
from wagtail import blocks

#: Section stack field names on page models, in render order. Consumed by the
#: page API serializer (``apps/pages/api.py``) to flatten each section's item
#: list onto the page payload.
SECTION_STACK_FIELDS = ["dna", "features", "steps", "stats", "pricing", "faq"]

#: For each section block type, the key of its nested *item list* that the API
#: flattens onto the page payload (e.g. ``pricing`` → ``tiers``).
SECTION_ITEM_LIST_KEYS = {
    "dna": "items",
    "features": "features",
    "steps": "steps",
    "stats": "stats",
    "pricing": "tiers",
    "faq": "items",
}


class LinkBlock(blocks.StructBlock):
    """A link with a label — internal page chooser wins over a manual URL."""

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
    """CTA button with the Loop-CRM styles (primary/secondary/outline)."""

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
        ],
        default="primary",
        label=_("Style"),
    )

    class Meta:
        icon = "placeholder"
        label = _("Button")


class HeroBlock(blocks.StructBlock):
    """Landing hero — eyebrow, headline + accent, lede, CTAs, footnote."""

    badge = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    accent = blocks.CharBlock(
        max_length=60,
        required=False,
        label=_("Accent word"),
        help_text=_("The emphasized word rendered with the accent mark (e.g. 'loop')."),
    )
    subtitle = blocks.TextBlock(required=False, label=_("Subtitle / lede"))
    primary_cta = ButtonBlock(required=False, label=_("Primary CTA"))
    secondary_cta = ButtonBlock(required=False, label=_("Secondary CTA"))
    note = blocks.CharBlock(
        max_length=200,
        required=False,
        label=_("Footnote"),
        help_text=_("Small mono line under the CTAs (e.g. heritage note)."),
    )

    class Meta:
        icon = "home"
        label = _("Hero")


class DnaItemBlock(blocks.StructBlock):
    """One DNA/heritage band cell (label + value)."""

    label = blocks.CharBlock(max_length=80, label=_("Label"))
    value = blocks.CharBlock(max_length=120, label=_("Value"))

    class Meta:
        icon = "placeholder"
        label = _("DNA item")


class DnaBandBlock(blocks.StructBlock):
    """Heritage strip — the label/value cells under the hero."""

    items = blocks.ListBlock(DnaItemBlock(), label=_("Items"))

    class Meta:
        icon = "list-ul"
        label = _("DNA band")


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

    title = blocks.CharBlock(max_length=200, required=False, label=_("Section title"))
    stats = blocks.ListBlock(StatBlock(), label=_("Stats"))

    class Meta:
        icon = "doc-full"
        label = _("Stats section")


class FeatureBlock(blocks.StructBlock):
    """A single module/feature card (icon key + title + description + link)."""

    icon = blocks.CharBlock(
        max_length=80,
        label=_("Icon"),
        help_text=_("Astro icon key (crm, marketing, attribution, …)."),
    )
    label = blocks.CharBlock(max_length=80, required=False, label=_("Kicker"))
    title = blocks.CharBlock(max_length=120, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    href = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_("URL"),
        help_text=_("Module URL (e.g. /crm/). Ignored when a page is chosen."),
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
    """Features/modules grid with a section heading."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    features = blocks.ListBlock(FeatureBlock(), label=_("Features"))

    class Meta:
        icon = "list-ul"
        label = _("Features section")


class StepBlock(blocks.StructBlock):
    """One numbered step in the 'how it works' band."""

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
