"""
Reusable Wagtail StreamField blocks for the landing-fusion pages.

Each block mirrors a section of the Astro frontend (src/components/blocks/*):
hero, stats, features, testimonials, pricing, faq, cta and contact info.
Templates live under ``apps/landing/templates/landing/blocks/`` and render the
same class names / Fusion tokens as the Astro side (see plan §5.1).
"""
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class LinkBlock(blocks.StructBlock):
    """A simple link with a label (used by buttons and footer links)."""

    label = blocks.CharBlock(max_length=80, label=_("Label"))
    href = blocks.CharBlock(max_length=255, required=False, label=_("URL"))

    class Meta:
        icon = "link"
        template = "landing/blocks/link.html"


class ButtonBlock(blocks.StructBlock):
    """CTA button with the four Fusion styles (primary/secondary/outline/white)."""

    label = blocks.CharBlock(max_length=80, label=_("Label"))
    href = blocks.CharBlock(max_length=255, required=False, label=_("URL"))
    style = blocks.ChoiceBlock(
        choices=[
            ("primary", _("Primary")),
            ("secondary", _("Secondary")),
            ("outline", _("Outline")),
            ("white", _("White")),
        ],
        default="primary",
        label=_("Style"),
    )

    class Meta:
        icon = "placeholder"
        template = "landing/blocks/button.html"


class HeroBlock(blocks.StructBlock):
    """Homepage hero — badge, headline, subtitle, CTAs and trusted-by line."""

    badge = blocks.CharBlock(max_length=80, required=False, label=_("Badge"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    subtitle = blocks.TextBlock(required=False, label=_("Subtitle"))
    primary_cta = ButtonBlock(required=False, label=_("Primary CTA"))
    secondary_cta = ButtonBlock(required=False, label=_("Secondary CTA"))
    trusted_by = blocks.CharBlock(
        max_length=160, required=False, label=_("Trusted-by text")
    )

    class Meta:
        icon = "home"
        label = _("Hero")
        template = "landing/blocks/hero.html"


class StatBlock(blocks.StructBlock):
    """A single KPI stat (value + suffix + label)."""

    value = blocks.CharBlock(max_length=20, label=_("Value"))
    suffix = blocks.CharBlock(max_length=10, required=False, label=_("Suffix"))
    label = blocks.CharBlock(max_length=120, label=_("Label"))

    class Meta:
        icon = "placeholder"
        template = "landing/blocks/stat.html"


class StatsSectionBlock(blocks.StructBlock):
    """Stats band — a row of animated counters."""

    title = blocks.CharBlock(max_length=200, required=False, label=_("Section title"))
    stats = blocks.ListBlock(StatBlock(), label=_("Stats"))

    class Meta:
        icon = "doc-full"
        label = _("Stats section")
        template = "landing/blocks/stats.html"


class FeatureBlock(blocks.StructBlock):
    """A single feature card (icon + title + description)."""

    icon = blocks.CharBlock(max_length=80, label=_("Icon"))
    title = blocks.CharBlock(max_length=120, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))

    class Meta:
        icon = "placeholder"
        template = "landing/blocks/feature.html"


class FeaturesSectionBlock(blocks.StructBlock):
    """Features grid with a section heading."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    features = blocks.ListBlock(FeatureBlock(), label=_("Features"))

    class Meta:
        icon = "list-ul"
        label = _("Features section")
        template = "landing/blocks/features.html"


class TestimonialBlock(blocks.StructBlock):
    """A single testimonial (quote + author + role + avatar initials)."""

    quote = blocks.TextBlock(label=_("Quote"))
    author = blocks.CharBlock(max_length=120, label=_("Author"))
    role = blocks.CharBlock(max_length=160, required=False, label=_("Role"))
    avatar_initials = blocks.CharBlock(
        max_length=4, required=False, label=_("Avatar initials")
    )

    class Meta:
        icon = "pick"
        template = "landing/blocks/testimonial.html"


class TestimonialsSectionBlock(blocks.StructBlock):
    """Testimonials carousel with section heading."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    testimonials = blocks.ListBlock(TestimonialBlock(), label=_("Testimonials"))

    class Meta:
        icon = "group"
        label = _("Testimonials section")
        template = "landing/blocks/testimonials.html"


class PricingTierBlock(blocks.StructBlock):
    """A pricing tier (name, price, features, CTA, featured flag)."""

    name = blocks.CharBlock(max_length=80, label=_("Name"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    price = blocks.CharBlock(max_length=20, label=_("Price"))
    period = blocks.CharBlock(max_length=40, required=False, label=_("Period"))
    features = blocks.ListBlock(blocks.CharBlock(max_length=160), label=_("Features"))
    cta_label = blocks.CharBlock(max_length=80, required=False, label=_("CTA label"))
    cta_href = blocks.CharBlock(max_length=255, required=False, label=_("CTA URL"))
    featured = blocks.BooleanBlock(required=False, default=False, label=_("Featured"))

    class Meta:
        icon = "placeholder"
        template = "landing/blocks/pricing_tier.html"


class PricingSectionBlock(blocks.StructBlock):
    """Pricing section with a heading and a list of tiers."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    tiers = blocks.ListBlock(PricingTierBlock(), label=_("Tiers"))

    class Meta:
        icon = "list-ul"
        label = _("Pricing section")
        template = "landing/blocks/pricing.html"


class FaqItemBlock(blocks.StructBlock):
    """A single FAQ accordion item."""

    question = blocks.CharBlock(max_length=200, label=_("Question"))
    answer = blocks.TextBlock(required=False, label=_("Answer"))

    class Meta:
        icon = "help"
        template = "landing/blocks/faq_item.html"


class FaqSectionBlock(blocks.StructBlock):
    """FAQ section with live search + accordion."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    items = blocks.ListBlock(FaqItemBlock(), label=_("FAQ items"))

    class Meta:
        icon = "help"
        label = _("FAQ section")
        template = "landing/blocks/faq.html"


class CtaBlock(blocks.StructBlock):
    """Full-width CTA banner (title + subtitle + buttons)."""

    title = blocks.CharBlock(max_length=200, label=_("Title"))
    subtitle = blocks.TextBlock(required=False, label=_("Subtitle"))
    primary_cta = ButtonBlock(required=False, label=_("Primary CTA"))
    secondary_cta = ButtonBlock(required=False, label=_("Secondary CTA"))

    class Meta:
        icon = "warning"
        label = _("CTA")
        template = "landing/blocks/cta.html"


class ContactMethodBlock(blocks.StructBlock):
    """A contact channel (email/phone/address/hours)."""

    method_type = blocks.ChoiceBlock(
        choices=[
            ("email", _("Email")),
            ("phone", _("Phone")),
            ("address", _("Address")),
            ("hours", _("Working hours")),
        ],
        default="email",
        label=_("Type"),
    )
    label = blocks.CharBlock(max_length=80, label=_("Label"))
    value = blocks.CharBlock(max_length=255, label=_("Value"))
    href = blocks.CharBlock(max_length=255, required=False, label=_("Link"))

    class Meta:
        icon = "placeholder"
        template = "landing/blocks/contact_method.html"


class ContactSectionBlock(blocks.StructBlock):
    """Contact page info + form intro."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    methods = blocks.ListBlock(ContactMethodBlock(), label=_("Contact methods"))
    form_title = blocks.CharBlock(
        max_length=200, required=False, label=_("Form title")
    )
    form_description = blocks.TextBlock(required=False, label=_("Form description"))

    class Meta:
        icon = "mail"
        label = _("Contact section")
        template = "landing/blocks/contact_section.html"
