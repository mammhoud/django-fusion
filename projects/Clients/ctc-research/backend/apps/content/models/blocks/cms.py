"""
Reusable StreamField blocks for Wagtail CMS pages.

These blocks match the block types in STATIC_PAGES so the API layer
can serve identical JSON whether content comes from Wagtail or the
static fallback.

Block types:
    hero, stats, rich_section, cta, faq_groups, contact_methods,
    section_header, form
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


# ═══════════════════════════════════════════════════════════════════
# CTA (Call-to-Action) link
# ═══════════════════════════════════════════════════════════════════

class CtaLinkBlock(blocks.StructBlock):
    """A single CTA link with label, href, and variant."""

    label = blocks.CharBlock(max_length=100, default="Learn More")
    href = blocks.CharBlock(max_length=300, default="/")
    variant = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("link", "Link"),
        ],
        default="primary",
    )

    class Meta:
        icon = "link"
        label = _("CTA Link")


# ═══════════════════════════════════════════════════════════════════
# Hero Block
# ═══════════════════════════════════════════════════════════════════

class HeroBlock(blocks.StructBlock):
    """Hero section with heading, intro, optional image, and CTAs."""

    heading = blocks.CharBlock(max_length=200, default="Welcome")
    intro = blocks.TextBlock(required=False, default="")
    image = ImageChooserBlock(required=False)
    ctas = blocks.ListBlock(CtaLinkBlock(), default=list)

    class Meta:
        icon = "title"
        label = _("Hero")
        template = "blocks/hero.html"


# ═══════════════════════════════════════════════════════════════════
# Stats / Counter Block
# ═══════════════════════════════════════════════════════════════════

class StatItemBlock(blocks.StructBlock):
    """A single stat/counter."""

    label = blocks.CharBlock(max_length=100, default="Students")
    value = blocks.CharBlock(max_length=50, default="0")
    description = blocks.CharBlock(max_length=200, required=False, default="")


class StatsBlock(blocks.StructBlock):
    """Row of stat/counter items."""

    items = blocks.ListBlock(StatItemBlock(), default=list)

    class Meta:
        icon = "order"
        label = _("Stats")


# ═══════════════════════════════════════════════════════════════════
# Section Header Block
# ═══════════════════════════════════════════════════════════════════

class SectionHeaderBlock(blocks.StructBlock):
    """Section header with optional CTA."""

    key = blocks.CharBlock(max_length=100, default="")
    heading = blocks.CharBlock(max_length=200, default="")
    intro = blocks.TextBlock(required=False, default="")
    cta = CtaLinkBlock(required=False)

    class Meta:
        icon = "header"
        label = _("Section Header")


# ═══════════════════════════════════════════════════════════════════
# Rich Section Block
# ═══════════════════════════════════════════════════════════════════

class RichSectionItemBlock(blocks.StructBlock):
    """An item within a rich section."""

    heading = blocks.CharBlock(max_length=200, default="")
    text = blocks.TextBlock(default="")


class RichSectionBlock(blocks.StructBlock):
    """Rich text section with heading, HTML, and item cards."""

    heading = blocks.CharBlock(max_length=200, default="")
    html = blocks.RichTextBlock(required=False, default="")
    items = blocks.ListBlock(RichSectionItemBlock(), default=list)

    class Meta:
        icon = "doc-full"
        label = _("Rich Section")


# ═══════════════════════════════════════════════════════════════════
# CTA Section Block
# ═══════════════════════════════════════════════════════════════════

class CtaBlock(blocks.StructBlock):
    """Call-to-action section with heading, intro, and CTAs."""

    heading = blocks.CharBlock(max_length=200, default="Get Started")
    intro = blocks.TextBlock(required=False, default="")
    ctas = blocks.ListBlock(CtaLinkBlock(), default=list)

    class Meta:
        icon = "success"
        label = _("Call to Action")


# ═══════════════════════════════════════════════════════════════════
# FAQ Block
# ═══════════════════════════════════════════════════════════════════

class FaqItemBlock(blocks.StructBlock):
    """A single FAQ question/answer pair."""

    question = blocks.CharBlock(max_length=300, default="")
    answer = blocks.TextBlock(default="")


class FaqGroupBlock(blocks.StructBlock):
    """A group of FAQ items under a category."""

    title = blocks.CharBlock(max_length=200, default="General")
    items = blocks.ListBlock(FaqItemBlock(), default=list)


class FaqGroupsBlock(blocks.StructBlock):
    """FAQ section with grouped categories."""

    groups = blocks.ListBlock(FaqGroupBlock(), default=list)

    class Meta:
        icon = "help"
        label = _("FAQ Groups")


# ═══════════════════════════════════════════════════════════════════
# Contact Methods Block
# ═══════════════════════════════════════════════════════════════════

class ContactMethodBlock(blocks.StructBlock):
    """A single contact method (email, phone, address, hours)."""

    type = blocks.ChoiceBlock(
        choices=[
            ("email", "Email"),
            ("phone", "Phone"),
            ("address", "Address"),
            ("hours", "Hours"),
        ],
        default="email",
    )
    label = blocks.CharBlock(max_length=100, default="Email")
    value = blocks.CharBlock(max_length=300, default="")
    href = blocks.CharBlock(max_length=300, required=False, default="")


class ContactMethodsBlock(blocks.StructBlock):
    """Contact methods section."""

    items = blocks.ListBlock(ContactMethodBlock(), default=list)

    class Meta:
        icon = "mail"
        label = _("Contact Methods")


# ═══════════════════════════════════════════════════════════════════
# Form Block
# ═══════════════════════════════════════════════════════════════════

class FormBlock(blocks.StructBlock):
    """Contact form indicator."""

    heading = blocks.CharBlock(max_length=200, default="Send us a message")

    class Meta:
        icon = "form"
        label = _("Form")


# ═══════════════════════════════════════════════════════════════════
# Dashboard Content Blocks
# ═══════════════════════════════════════════════════════════════════

class DashboardWelcomeBlock(blocks.StructBlock):
    """Welcome greeting block for the dashboard header."""

    heading = blocks.CharBlock(max_length=200, default="Welcome back!")
    intro = blocks.TextBlock(required=False, default="")
    icon_class = blocks.CharBlock(max_length=100, required=False, default="")

    class Meta:
        icon = "user"
        label = _("Dashboard Welcome")


class DashboardQuickLinkBlock(blocks.StructBlock):
    """A single quick-link item for the dashboard."""

    label = blocks.CharBlock(max_length=100, default="My Courses")
    href = blocks.CharBlock(max_length=300, default="/dashboard/courses")
    icon_class = blocks.CharBlock(max_length=100, required=False, default="")
    sort_order = blocks.IntegerBlock(default=0)


class DashboardQuickLinksBlock(blocks.StructBlock):
    """Quick-link section for the dashboard sidebar or homepage."""

    heading = blocks.CharBlock(max_length=200, required=False, default="Quick Links")
    links = blocks.ListBlock(DashboardQuickLinkBlock(), default=list)

    class Meta:
        icon = "link"
        label = _("Dashboard Quick Links")


class DashboardTipBlock(blocks.StructBlock):
    """A tip / helpful hint displayed on the dashboard."""

    heading = blocks.CharBlock(max_length=200, default="Tip")
    content = blocks.TextBlock(default="")
    icon_class = blocks.CharBlock(max_length=100, required=False, default="")

    class Meta:
        icon = "pick"
        label = _("Dashboard Tip")


class DashboardAnnouncementBlock(blocks.StructBlock):
    """A CMS-managed inline announcement block for the dashboard."""

    heading = blocks.CharBlock(max_length=200, default="Announcement")
    content = blocks.TextBlock(default="")
    link = blocks.CharBlock(max_length=300, required=False, default="")
    link_label = blocks.CharBlock(max_length=100, required=False, default="Learn More")
    variant = blocks.ChoiceBlock(
        choices=[
            ("info", "Info"),
            ("warning", "Warning"),
            ("success", "Success"),
        ],
        default="info",
    )

    class Meta:
        icon = "warning"
        label = _("Dashboard Announcement")


# ═══════════════════════════════════════════════════════════════════
# Dashboard Page Block Registry
# ═══════════════════════════════════════════════════════════════════

DASHBOARD_CONTENT_BLOCKS = [
    ("dashboard_welcome", DashboardWelcomeBlock()),
    ("dashboard_quick_links", DashboardQuickLinksBlock()),
    ("dashboard_tip", DashboardTipBlock()),
    ("dashboard_announcement", DashboardAnnouncementBlock()),
]


# ═══════════════════════════════════════════════════════════════════
# Slider Block (reusable — hero/carousel on any page)
# ═══════════════════════════════════════════════════════════════════

class SliderSlideBlock(blocks.StructBlock):
    """A single slide: image, subtitle, title, description, and optional CTA."""

    image = ImageChooserBlock(required=False, label=_("Image"))
    subtitle = blocks.CharBlock(required=False, max_length=150, label=_("Subtitle"))
    title = blocks.CharBlock(required=True, max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, max_length=400, label=_("Description"))
    text_alignment = blocks.ChoiceBlock(
        choices=[
            ("left", _("Left")),
            ("center", _("Center")),
            ("right", _("Right")),
        ],
        default="left",
        required=False,
        label=_("Text Alignment"),
    )
    button_text = blocks.CharBlock(required=False, max_length=50, label=_("Button Text"))
    button_link = blocks.URLBlock(required=False, label=_("Button Link"))
    alt_text = blocks.CharBlock(required=False, max_length=200, label=_("Alt Text"))

    class Meta:
        icon = "images"
        label = _("Slide")


class SliderBlock(blocks.StructBlock):
    """Swiper-style carousel: loop, autoplay, navigation, and dots.

    Renders server-side (no-JS shows the full strip) and enhances with
    Alpine when available — mirrors the frontend course-slider contract.
    """

    heading = blocks.CharBlock(required=False, max_length=200, label=_("Heading"))
    intro = blocks.TextBlock(required=False, max_length=400, label=_("Intro"))
    slides = blocks.ListBlock(SliderSlideBlock(), label=_("Slides"))

    # Swiper-style options
    loop = blocks.BooleanBlock(default=True, required=False, label=_("Loop"), help_text=_("Wrap around at the end"))
    autoplay = blocks.BooleanBlock(default=True, required=False, label=_("Autoplay"))
    autoplay_interval = blocks.IntegerBlock(default=7000, min_value=1000, max_value=30000, required=False, label=_("Autoplay Interval (ms)"))
    show_navigation = blocks.BooleanBlock(default=True, required=False, label=_("Show Arrows"))
    show_dots = blocks.BooleanBlock(default=True, required=False, label=_("Show Dots"))
    per_view = blocks.ChoiceBlock(
        choices=[
            (1, "1"),
            (2, "2"),
            (3, "3"),
        ],
        default=1,
        required=False,
        label=_("Slides Per View"),
        help_text=_("Desktop slides per view (mobile always shows 1)"),
    )

    class Meta:
        icon = "images"
        label = _("Slider")
        template = "blocks/slider.html"
        group = _("Media")


# ═══════════════════════════════════════════════════════════════════
# Global StreamBlock (used by all page types)
# ═══════════════════════════════════════════════════════════════════

PAGE_CONTENT_BLOCKS = [
    ("hero", HeroBlock()),
    ("slider", SliderBlock()),
    ("stats", StatsBlock()),
    ("section_header", SectionHeaderBlock()),
    ("rich_section", RichSectionBlock()),
    ("cta", CtaBlock()),
    ("faq_groups", FaqGroupsBlock()),
    ("contact_methods", ContactMethodsBlock()),
    ("form", FormBlock()),
]
