"""
Reusable StreamField blocks for Wagtail CMS pages.

These blocks match the block types in STATIC_PAGES so the API layer
can serve identical JSON whether content comes from Wagtail or the
static fallback.

Block types:
    hero, stats, rich_section, cta, faq_groups, contact_methods,
    section_header, form, testimonials, clients, pricing, services_grid,
    team_grid, feature_grid, newsletter, video_embed, page_title
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
# Testimonials Block
# ═══════════════════════════════════════════════════════════════════

class TestimonialBlock(blocks.StructBlock):
    """A single testimonial."""

    name = blocks.CharBlock(max_length=100, default="John Doe")
    role = blocks.CharBlock(max_length=100, required=False, default="")
    company = blocks.CharBlock(max_length=100, required=False, default="")
    quote = blocks.TextBlock(default="Great experience!")
    avatar = ImageChooserBlock(required=False)
    rating = blocks.IntegerBlock(min_value=1, max_value=5, default=5, required=False)

    class Meta:
        icon = "openquote"
        label = _("Testimonial")


class TestimonialsBlock(blocks.StructBlock):
    """Testimonials section with carousel/grid display."""

    heading = blocks.CharBlock(max_length=200, default="What Our Clients Say")
    intro = blocks.TextBlock(required=False, default="")
    items = blocks.ListBlock(TestimonialBlock(), default=list)
    display_style = blocks.ChoiceBlock(
        choices=[("carousel", "Carousel"), ("grid", "Grid"), ("masonry", "Masonry")],
        default="carousel",
        required=False,
    )

    class Meta:
        icon = "group"
        label = _("Testimonials")
        template = "blocks/testimonials.html"


# ═══════════════════════════════════════════════════════════════════
# Clients / Partners Block
# ═══════════════════════════════════════════════════════════════════

class ClientBlock(blocks.StructBlock):
    """A single client/partner logo + info."""

    name = blocks.CharBlock(max_length=100, default="Client Name")
    logo = ImageChooserBlock(required=False)
    url = blocks.URLBlock(required=False)
    description = blocks.TextBlock(required=False, default="")

    class Meta:
        icon = "site"
        label = _("Client")


class ClientsBlock(blocks.StructBlock):
    """Client/partner logo grid section."""

    heading = blocks.CharBlock(max_length=200, default="Trusted By")
    intro = blocks.TextBlock(required=False, default="")
    items = blocks.ListBlock(ClientBlock(), default=list)
    columns = blocks.IntegerBlock(min_value=2, max_value=6, default=4, required=False)

    class Meta:
        icon = "group"
        label = _("Clients / Partners")
        template = "blocks/clients.html"


# ═══════════════════════════════════════════════════════════════════
# Pricing Block
# ═══════════════════════════════════════════════════════════════════

class PricingFeatureBlock(blocks.StructBlock):
    """A single feature/checkbox in a pricing tier."""

    text = blocks.CharBlock(max_length=200, default="Feature")
    included = blocks.BooleanBlock(default=True, required=False)


class PricingTierBlock(blocks.StructBlock):
    """A single pricing tier."""

    name = blocks.CharBlock(max_length=100, default="Basic")
    price = blocks.CharBlock(max_length=50, default="$0")
    period = blocks.CharBlock(max_length=50, default="/month", required=False)
    description = blocks.TextBlock(required=False, default="")
    features = blocks.ListBlock(PricingFeatureBlock(), default=list)
    cta = CtaLinkBlock(required=False)
    highlighted = blocks.BooleanBlock(default=False, required=False)
    badge = blocks.CharBlock(max_length=50, required=False, default="")

    class Meta:
        icon = "tag"
        label = _("Pricing Tier")


class PricingBlock(blocks.StructBlock):
    """Pricing table section."""

    heading = blocks.CharBlock(max_length=200, default="Pricing Plans")
    intro = blocks.TextBlock(required=False, default="")
    tiers = blocks.ListBlock(PricingTierBlock(), default=list)
    currency_symbol = blocks.CharBlock(max_length=5, default="$", required=False)

    class Meta:
        icon = "dollar"
        label = _("Pricing Table")
        template = "blocks/pricing.html"


# ═══════════════════════════════════════════════════════════════════
# Services Grid Block
# ═══════════════════════════════════════════════════════════════════

class ServiceCardBlock(blocks.StructBlock):
    """A single service card."""

    icon_class = blocks.CharBlock(max_length=100, default="bi bi-star", required=False)
    title = blocks.CharBlock(max_length=100, default="Service")
    description = blocks.TextBlock(default="")
    url = blocks.CharBlock(max_length=300, required=False, default="")
    image = ImageChooserBlock(required=False)

    class Meta:
        icon = "cog"
        label = _("Service Card")


class ServicesGridBlock(blocks.StructBlock):
    """Services grid section."""

    heading = blocks.CharBlock(max_length=200, default="Our Services")
    intro = blocks.TextBlock(required=False, default="")
    items = blocks.ListBlock(ServiceCardBlock(), default=list)
    columns = blocks.IntegerBlock(min_value=1, max_value=4, default=3, required=False)

    class Meta:
        icon = "list-ul"
        label = _("Services Grid")
        template = "blocks/services_grid.html"


# ═══════════════════════════════════════════════════════════════════
# Team Grid Block
# ═══════════════════════════════════════════════════════════════════

class TeamMemberBlock(blocks.StructBlock):
    """A single team member."""

    name = blocks.CharBlock(max_length=100, default="Jane Smith")
    role = blocks.CharBlock(max_length=100, default="Developer")
    bio = blocks.TextBlock(required=False, default="")
    photo = ImageChooserBlock(required=False)
    email = blocks.EmailBlock(required=False)
    socials = blocks.StreamBlock(
        [
            ("social", blocks.StructBlock(
                [
                    ("platform", blocks.ChoiceBlock(
                        choices=[(p[0], p[1]) for p in [
                            ("twitter", "Twitter"), ("linkedin", "LinkedIn"),
                            ("github", "GitHub"), ("website", "Website"),
                            ("facebook", "Facebook"), ("instagram", "Instagram"),
                        ]],
                        default="linkedin",
                    )),
                    ("url", blocks.URLBlock(default="")),
                ],
                icon="link",
                label=_("Social Link"),
            )),
        ],
        required=False,
    )

    class Meta:
        icon = "user"
        label = _("Team Member")


class TeamGridBlock(blocks.StructBlock):
    """Team members grid section."""

    heading = blocks.CharBlock(max_length=200, default="Meet Our Team")
    intro = blocks.TextBlock(required=False, default="")
    members = blocks.ListBlock(TeamMemberBlock(), default=list)
    columns = blocks.IntegerBlock(min_value=2, max_value=4, default=3, required=False)

    class Meta:
        icon = "group"
        label = _("Team Grid")
        template = "blocks/team_grid.html"


# ═══════════════════════════════════════════════════════════════════
# Feature Grid Block
# ═══════════════════════════════════════════════════════════════════

class FeatureItemBlock(blocks.StructBlock):
    """A single feature card."""

    icon_class = blocks.CharBlock(max_length=100, default="bi bi-check-circle")
    title = blocks.CharBlock(max_length=100, default="Feature")
    description = blocks.TextBlock(default="")

    class Meta:
        icon = "check"
        label = _("Feature Item")


class FeatureGridBlock(blocks.StructBlock):
    """Feature grid section."""

    heading = blocks.CharBlock(max_length=200, default="Why Choose Us")
    intro = blocks.TextBlock(required=False, default="")
    items = blocks.ListBlock(FeatureItemBlock(), default=list)
    columns = blocks.IntegerBlock(min_value=2, max_value=4, default=3, required=False)

    class Meta:
        icon = "th-list"
        label = _("Feature Grid")
        template = "blocks/feature_grid.html"


# ═══════════════════════════════════════════════════════════════════
# Newsletter Block
# ═══════════════════════════════════════════════════════════════════

class NewsletterBlock(blocks.StructBlock):
    """Newsletter signup form section."""

    heading = blocks.CharBlock(max_length=200, default="Stay Updated")
    description = blocks.TextBlock(required=False, default="Subscribe to our newsletter for the latest updates.")
    placeholder = blocks.CharBlock(max_length=100, default="your@email.com", required=False)
    button_label = blocks.CharBlock(max_length=50, default="Subscribe", required=False)
    provider = blocks.ChoiceBlock(
        choices=[("native", "Native (django-fusion)"), ("mailchimp", "Mailchimp"), ("convertkit", "ConvertKit")],
        default="native",
    )
    form_action = blocks.CharBlock(max_length=300, required=False, default="/htmx/newsletter/")

    class Meta:
        icon = "mail"
        label = _("Newsletter Signup")
        template = "blocks/newsletter.html"


# ═══════════════════════════════════════════════════════════════════
# Video Embed Block
# ═══════════════════════════════════════════════════════════════════

class VideoEmbedBlock(blocks.StructBlock):
    """Embedded video section."""

    title = blocks.CharBlock(max_length=200, required=False, default="")
    url = blocks.URLBlock(default="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    poster_image = ImageChooserBlock(required=False)
    aspect_ratio = blocks.ChoiceBlock(
        choices=[("16/9", "16:9"), ("4/3", "4:3"), ("1/1", "1:1"), ("21/9", "21:9")],
        default="16/9",
        required=False,
    )
    description = blocks.TextBlock(required=False, default="")

    class Meta:
        icon = "media"
        label = _("Video Embed")
        template = "blocks/video_embed.html"


# ═══════════════════════════════════════════════════════════════════
# Page Title / Breadcrumb Block
# ═══════════════════════════════════════════════════════════════════

class PageTitleBlock(blocks.StructBlock):
    """Page title hero with breadcrumb."""

    heading = blocks.CharBlock(max_length=200, default="Page Title")
    intro = blocks.TextBlock(required=False, default="")
    background_image = ImageChooserBlock(required=False)
    show_breadcrumb = blocks.BooleanBlock(default=True, required=False)

    class Meta:
        icon = "title"
        label = _("Page Title")
        template = "blocks/page_title.html"


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
# Global StreamBlock (used by all page types)
# ═══════════════════════════════════════════════════════════════════

PAGE_CONTENT_BLOCKS = [
    ("hero", HeroBlock()),
    ("stats", StatsBlock()),
    ("page_title", PageTitleBlock()),
    ("section_header", SectionHeaderBlock()),
    ("rich_section", RichSectionBlock()),
    ("feature_grid", FeatureGridBlock()),
    ("testimonials", TestimonialsBlock()),
    ("clients", ClientsBlock()),
    ("services_grid", ServicesGridBlock()),
    ("team_grid", TeamGridBlock()),
    ("pricing", PricingBlock()),
    ("cta", CtaBlock()),
    ("faq_groups", FaqGroupsBlock()),
    ("contact_methods", ContactMethodsBlock()),
    ("form", FormBlock()),
    ("newsletter", NewsletterBlock()),
    ("video_embed", VideoEmbedBlock()),
]
