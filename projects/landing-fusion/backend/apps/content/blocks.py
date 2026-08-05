# Section stack field names — shared between models and the API serializer.
# Any page model that carries these fields exports their content via
# the /apis/pages/<slug>/ endpoint.
SECTION_STACK_FIELDS = [
    "stats", "features", "testimonials", "pricing", "faq", "projects",
    "services", "process", "blog",
    "tech", "editions", "snippets",
]


"""
Reusable Wagtail StreamField blocks for the landing-fusion pages.

Each block mirrors a section of the Astro frontend (src/components/blocks/*):
hero, stats, features, testimonials, pricing, faq, cta and contact info.
Templates live under ``apps/content/templates/content/blocks/`` and render the
same class names / Fusion tokens as the Astro side (see plan §5.1).
"""
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ProjectFeatureBlock(blocks.StructBlock):
    """A single feature of a project, flagged shared (reused across the monorepo) or standalone."""

    label = blocks.CharBlock(max_length=160, label=_("Feature"))
    shared = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Shared across the repo"),
        help_text=_("Tick when this capability is reused by other projects in the monorepo."),
    )

    class Meta:
        icon = "placeholder"
        label = _("Project feature")
        template = "content/blocks/project_feature.html"


class ProjectBlock(blocks.StructBlock):
    """A repo project card — name, edition, category, path, and shared/standalone features."""

    name = blocks.CharBlock(max_length=120, label=_("Name"))
    edition = blocks.CharBlock(
        max_length=80,
        required=False,
        label=_("Edition"),
        help_text=_("e.g. Minimal / Solo / Full for the POS editions."),
    )
    category = blocks.ChoiceBlock(
        choices=[
            ("website", _("Website")),
            ("product", _("Product")),
            ("library", _("Library")),
            ("infra", _("Infrastructure")),
        ],
        default="website",
        label=_("Category"),
    )
    path = blocks.CharBlock(max_length=255, required=False, label=_("Repo path"))
    url = blocks.CharBlock(max_length=255, required=False, label=_("URL"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    features = blocks.ListBlock(ProjectFeatureBlock(), label=_("Features"))

    class Meta:
        icon = "folder-open-inverse"
        label = _("Project")
        template = "content/blocks/project.html"


class LinkBlock(blocks.StructBlock):
    """A simple link with a label (used by buttons and footer links)."""

    label = blocks.CharBlock(max_length=80, label=_("Label"))
    href = blocks.CharBlock(max_length=255, required=False, label=_("URL"))

    class Meta:
        icon = "link"
        template = "content/blocks/link.html"


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
        template = "content/blocks/button.html"


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
        template = "content/blocks/hero.html"


class StatBlock(blocks.StructBlock):
    """A single KPI stat (value + suffix + label)."""

    value = blocks.CharBlock(max_length=20, label=_("Value"))
    suffix = blocks.CharBlock(max_length=10, required=False, label=_("Suffix"))
    label = blocks.CharBlock(max_length=120, label=_("Label"))

    class Meta:
        icon = "placeholder"
        template = "content/blocks/stat.html"


class StatsSectionBlock(blocks.StructBlock):
    """Stats band — a row of animated counters."""

    title = blocks.CharBlock(max_length=200, required=False, label=_("Section title"))
    stats = blocks.ListBlock(StatBlock(), label=_("Stats"))

    class Meta:
        icon = "doc-full"
        label = _("Stats section")
        template = "content/blocks/stats.html"


class FeatureBlock(blocks.StructBlock):
    """A single feature card (icon + title + description)."""

    icon = blocks.CharBlock(max_length=80, label=_("Icon"))
    title = blocks.CharBlock(max_length=120, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))

    class Meta:
        icon = "placeholder"
        template = "content/blocks/feature.html"


class FeaturesSectionBlock(blocks.StructBlock):
    """Features grid with a section heading."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    features = blocks.ListBlock(FeatureBlock(), label=_("Features"))

    class Meta:
        icon = "list-ul"
        label = _("Features section")
        template = "content/blocks/features.html"


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
        template = "content/blocks/testimonial.html"


class TestimonialsSectionBlock(blocks.StructBlock):
    """Testimonials carousel with section heading."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    testimonials = blocks.ListBlock(TestimonialBlock(), label=_("Testimonials"))

    class Meta:
        icon = "group"
        label = _("Testimonials section")
        template = "content/blocks/testimonials.html"


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
        template = "content/blocks/pricing_tier.html"


class PricingSectionBlock(blocks.StructBlock):
    """Pricing section with a heading and a list of tiers."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    tiers = blocks.ListBlock(PricingTierBlock(), label=_("Tiers"))

    class Meta:
        icon = "list-ul"
        label = _("Pricing section")
        template = "content/blocks/pricing.html"


class FaqItemBlock(blocks.StructBlock):
    """A single FAQ accordion item."""

    question = blocks.CharBlock(max_length=200, label=_("Question"))
    answer = blocks.TextBlock(required=False, label=_("Answer"))

    class Meta:
        icon = "help"
        template = "content/blocks/faq_item.html"


class FaqSectionBlock(blocks.StructBlock):
    """FAQ section with live search + accordion."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    items = blocks.ListBlock(FaqItemBlock(), label=_("FAQ items"))

    class Meta:
        icon = "help"
        label = _("FAQ section")
        template = "content/blocks/faq.html"


class ProcessStepBlock(blocks.StructBlock):
    """A single numbered 'build as you go' step (discovery → ship → grow)."""

    title = blocks.CharBlock(max_length=120, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    deliverable = blocks.CharBlock(
        max_length=200, required=False, label=_("Deliverable"),
        help_text=_("What you walk away with at the end of this step."),
    )

    class Meta:
        icon = "placeholder"
        label = _("Process step")
        template = "content/blocks/process_step.html"


class ProcessSectionBlock(blocks.StructBlock):
    """'Build as you go' section — a numbered process/steps band.

    Steps are rendered in order (1, 2, 3 …) so editors can reorder them
    freely without maintaining numbers by hand.
    """

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    steps = blocks.ListBlock(ProcessStepBlock(), label=_("Steps"))

    class Meta:
        icon = "list-ol"
        label = _("Process section")
        template = "content/blocks/process.html"


class ServiceBlock(blocks.StructBlock):
    """A single service offering card (icon + title + description + deliverables)."""

    icon = blocks.CharBlock(max_length=80, label=_("Icon"))
    title = blocks.CharBlock(max_length=120, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    deliverables = blocks.ListBlock(
        blocks.CharBlock(max_length=200), label=_("Deliverables")
    )
    cta_label = blocks.CharBlock(max_length=80, required=False, label=_("CTA label"))
    cta_href = blocks.CharBlock(max_length=255, required=False, label=_("CTA URL"))

    class Meta:
        icon = "placeholder"
        label = _("Service")
        template = "content/blocks/service.html"


class ServicesSectionBlock(blocks.StructBlock):
    """Services grid with a section heading (used by the Services page)."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    services = blocks.ListBlock(ServiceBlock(), label=_("Services"))

    class Meta:
        icon = "list-ul"
        label = _("Services section")
        template = "content/blocks/services.html"


class BlogPostBlock(blocks.StructBlock):
    """A single blog post card (meta + excerpt, links to the live post)."""

    title = blocks.CharBlock(max_length=200, label=_("Title"))
    slug = blocks.CharBlock(
        max_length=200, required=False, label=_("Slug"),
        help_text=_("URL slug — links the card to /blog/<slug>/."),
    )
    category = blocks.CharBlock(max_length=80, required=False, label=_("Category"))
    date = blocks.DateBlock(required=False, label=_("Date"))
    read_time = blocks.CharBlock(
        max_length=40, required=False, label=_("Read time")
    )
    excerpt = blocks.TextBlock(required=False, label=_("Excerpt"))

    class Meta:
        icon = "doc-full-inverse"
        label = _("Blog post")
        template = "content/blocks/blog_post.html"


class BlogSectionBlock(blocks.StructBlock):
    """Blog grid — a heading plus a list of post cards (Blog page)."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    posts = blocks.ListBlock(BlogPostBlock(), label=_("Posts"))

    class Meta:
        icon = "doc-full-inverse"
        label = _("Blog section")
        template = "content/blocks/blog.html"


class CtaBlock(blocks.StructBlock):
    """Full-width CTA banner (title + subtitle + buttons)."""

    title = blocks.CharBlock(max_length=200, label=_("Title"))
    subtitle = blocks.TextBlock(required=False, label=_("Subtitle"))
    primary_cta = ButtonBlock(required=False, label=_("Primary CTA"))
    secondary_cta = ButtonBlock(required=False, label=_("Secondary CTA"))

    class Meta:
        icon = "warning"
        label = _("CTA")
        template = "content/blocks/cta.html"


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
        template = "content/blocks/contact_method.html"


class TechStackSectionBlock(blocks.StructBlock):
    """Technology stack band — the tools a product is built on (tags)."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    items = blocks.ListBlock(blocks.CharBlock(max_length=80), label=_("Technologies"))

    class Meta:
        icon = "cog"
        label = _("Tech stack")
        template = "content/blocks/tech_stack.html"


class EditionBlock(blocks.StructBlock):
    """A single product edition — a pricing tier with its own feature set.

    Used by product pages so each product lists its editions (e.g. Forge POS:
    Minimal · Solo · Full) with pricing and the capabilities that ship in that
    edition only.
    """

    name = blocks.CharBlock(max_length=80, label=_("Name"))
    tagline = blocks.TextBlock(required=False, label=_("Tagline"))
    price = blocks.CharBlock(max_length=20, label=_("Price"))
    period = blocks.CharBlock(max_length=40, required=False, label=_("Period"))
    features = blocks.ListBlock(blocks.CharBlock(max_length=200), label=_("Features"))
    cta_label = blocks.CharBlock(max_length=80, required=False, label=_("CTA label"))
    cta_href = blocks.CharBlock(max_length=255, required=False, label=_("CTA URL"))
    featured = blocks.BooleanBlock(required=False, default=False, label=_("Featured"))

    class Meta:
        icon = "placeholder"
        label = _("Edition")
        template = "content/blocks/edition.html"


class EditionsSectionBlock(blocks.StructBlock):
    """Editions & pricing section — per-product pricing with edition cards."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    editions = blocks.ListBlock(EditionBlock(), label=_("Editions"))

    class Meta:
        icon = "list-ul"
        label = _("Editions & pricing")
        template = "content/blocks/editions.html"


class SnippetBlock(blocks.StructBlock):
    """A reference code/model snippet — the 'use as a reference' building block.

    Pairs a title with a code block (e.g. a Rust struct, a SQLite schema, a
    Wagtail model) so a product page doubles as a reference for other projects
    (e.g. LMS reusing Forge POS patterns).
    """

    title = blocks.CharBlock(max_length=200, label=_("Title"))
    language = blocks.CharBlock(max_length=40, required=False, label=_("Language"))
    code = blocks.TextBlock(label=_("Code"), help_text=_("The snippet body — kept verbatim."))

    class Meta:
        icon = "code"
        label = _("Snippet")
        template = "content/blocks/snippet.html"


class SnippetsSectionBlock(blocks.StructBlock):
    """Reference snippets section — code + models other projects can copy from."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    snippets = blocks.ListBlock(SnippetBlock(), label=_("Snippets"))

    class Meta:
        icon = "code"
        label = _("Snippets section")
        template = "content/blocks/snippets.html"


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
        template = "content/blocks/contact_section.html"
