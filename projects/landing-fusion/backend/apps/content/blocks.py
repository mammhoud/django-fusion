# Section stack field names — shared between models and the API serializer.
# Any page model that carries these fields exports their content via
# the /apis/pages/<slug>/ endpoint.
SECTION_STACK_FIELDS = [
    "stats", "features", "testimonials", "pricing", "faq", "projects",
    "services", "process", "blog",
    "tech", "editions", "snippets", "comparison", "team", "gallery",
]


"""
Reusable Wagtail StreamField blocks for the landing-fusion pages.

Each block mirrors a section of the Astro frontend (src/components/blocks/*):
hero, stats, features, testimonials, pricing, faq, cta and contact info.
Templates live under ``apps/content/templates/content/blocks/`` and render the
same class names / Fusion tokens as the Astro side (see plan §5.1).
"""
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
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
        help_text=_("e.g. Community / Standard / Pro / Cloud for the POS editions."),
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
    """A simple link with a label (used by buttons and footer links).

    Editors can pick an internal Wagtail page (``page``) or type a manual
    URL (``href``). The chosen page always wins — its live URL replaces the
    manual one at render/API time, so links never go stale when a page moves.
    """

    label = blocks.CharBlock(max_length=80, label=_("Label"))
    href = blocks.CharBlock(max_length=255, required=False, label=_("URL"), help_text=_(
        "External URL (e.g. https://github.com/…). Ignored when a page is chosen."
    ))
    page = blocks.PageChooserBlock(
        required=False,
        label=_("Link to a page"),
        help_text=_("Pick an internal page — its URL wins over the manual URL field."),
    )

    class Meta:
        icon = "link"
        template = "content/blocks/link.html"


class ButtonBlock(blocks.StructBlock):
    """CTA button with the four Fusion styles (primary/secondary/outline/white).

    The label is optional when a page is chosen — the linked page's title
    becomes the button's visible text (the button's "header"). Editors can
    override it at any time by typing a custom label.
    """

    label = blocks.CharBlock(
        max_length=80,
        required=False,
        label=_("Label"),
        help_text=_("Leave empty to use the linked page's title."),
    )
    href = blocks.CharBlock(max_length=255, required=False, label=_("URL"), help_text=_(
        "External URL (e.g. https://github.com/…). Ignored when a page is chosen."
    ))
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
            ("white", _("White")),
        ],
        default="primary",
        label=_("Style"),
    )

    class Meta:
        icon = "placeholder"
        template = "content/blocks/button.html"


class HeroBlock(blocks.StructBlock):
    """Homepage hero — badge, headline + accent, subtitle, CTAs and trusted-by line.

    ``title`` and ``accent`` render separately (mirroring the Astro Hero
    component's ``heading`` + ``accent`` props): the accent word gets the
    highlighter-mark treatment, so keep it short ("documents", "السوق").
    """

    badge = blocks.CharBlock(max_length=80, required=False, label=_("Badge"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    accent = blocks.CharBlock(
        max_length=60,
        required=False,
        label=_("Accent word"),
        help_text=_(
            "The emphasized word rendered with the highlighter mark (e.g. "
            "'documents'). One or two words — not part of the title."
        ),
    )
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
    cta_page = blocks.PageChooserBlock(
        required=False,
        label=_("CTA page"),
        help_text=_("Pick an internal page instead of typing a CTA URL."),
    )
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
    cta_page = blocks.PageChooserBlock(
        required=False,
        label=_("CTA page"),
        help_text=_("Pick an internal page instead of typing a CTA URL."),
    )

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
    page = blocks.PageChooserBlock(
        required=False,
        label=_("Linked post"),
        help_text=_("Pick the BlogPostPage instead of typing a slug — its URL wins."),
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
    href = blocks.CharBlock(max_length=255, required=False, label=_("Link"), help_text=_(
        "External link (mailto:, tel:, https://…). Ignored when a page is chosen."
    ))
    page = blocks.PageChooserBlock(
        required=False,
        label=_("Link to a page"),
        help_text=_("Pick an internal page instead of typing a link."),
    )

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


class EditionPreviewImageBlock(blocks.StructBlock):
    """A labelled product capture shown on an edition preview page.

    URLs intentionally point at static assets rather than Wagtail image IDs so
    the Django and Astro render roads share the same portable contract and
    build without a database/media lookup. The media kind is validated here,
    at the editor boundary, so a video can never silently become a broken
    ``<img>`` element on one render road.
    """

    _VIDEO_SUFFIXES = {".mp4", ".webm", ".ogv"}
    _IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}

    url = blocks.CharBlock(
        max_length=255,
        label=_("Media URL"),
        help_text=_("Use a site static URL, for example /static/previews/formints/standard-front.jpg."),
    )
    kind = blocks.ChoiceBlock(
        choices=[
            ("image", _("Image")),
            ("gif", _("Animated GIF")),
            ("video", _("Video")),
        ],
        default="image",
        label=_("Media type"),
        help_text=_("Use GIF for a walkthrough. Use Video for an MP4/WebM recording."),
    )
    poster = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_("Video poster"),
        help_text=_("Optional static poster path for video. Use /static/... or a relative previews/... path."),
    )
    label = blocks.CharBlock(max_length=80, required=False, label=_("View label"))
    alt = blocks.CharBlock(max_length=160, required=False, label=_("Alt text"))

    def clean(self, value):
        """Validate the media contract before it reaches a live revision."""
        cleaned = super().clean(value)
        url = str(cleaned.get("url", "")).strip()
        kind = str(cleaned.get("kind", "image"))
        path = urlsplit(url).path.lower()
        suffix = ""
        for candidate in self._VIDEO_SUFFIXES | self._IMAGE_SUFFIXES:
            if path.endswith(candidate):
                suffix = candidate
                break

        errors = {}
        if kind == "video" and suffix not in self._VIDEO_SUFFIXES:
            errors["url"] = ValidationError(
                _("Video previews must use an MP4, WebM, or OGV URL.")
            )
        elif kind == "gif" and suffix != ".gif":
            errors["url"] = ValidationError(
                _("Animated GIF previews must use a .gif URL.")
            )
        elif kind == "image" and suffix in self._VIDEO_SUFFIXES:
            errors["kind"] = ValidationError(
                _("Choose Video for MP4, WebM, or OGV media.")
            )

        poster = str(cleaned.get("poster", "")).strip()
        if poster and kind != "video":
            errors["poster"] = ValidationError(
                _("A poster is only used with Video previews.")
            )

        if errors:
            raise blocks.StructBlockValidationError(block_errors=errors)
        return cleaned

    class Meta:
        icon = "image"
        label = _("Preview image")


class EditionBlock(blocks.StructBlock):
    """A single product edition — a pricing tier with its own feature set.

    Used by product pages so each product lists its editions (e.g. Formints:
    Community · Standard · Pro · Cloud) with pricing and the capabilities
    that ship in that edition only.
    """

    name = blocks.CharBlock(max_length=80, label=_("Name"))
    tagline = blocks.TextBlock(required=False, label=_("Tagline"))
    price = blocks.CharBlock(max_length=20, label=_("Price"))
    period = blocks.CharBlock(max_length=40, required=False, label=_("Period"))
    features = blocks.ListBlock(blocks.CharBlock(max_length=200), label=_("Features"))
    preview_images = blocks.ListBlock(
        EditionPreviewImageBlock(),
        required=False,
        max_num=4,
        label=_("Preview images"),
        help_text=_("Optional screenshots shown on the edition preview page. Keep the list to the most useful product views."),
    )
    offer_label = blocks.CharBlock(
        max_length=60,
        required=False,
        label=_("Offer badge"),
        help_text=_(
            "Short deal/discount chip shown on the card (e.g. '50% off · launch'). "
            "Works on any edition — course, special, or standard."
        ),
    )
    offer_old_price = blocks.CharBlock(
        max_length=20,
        required=False,
        label=_("Old price"),
        help_text=_(
            "Original price struck through next to the current price (e.g. '$158'). "
            "Keep it short — the price row stays on one line."
        ),
    )
    cta_label = blocks.CharBlock(max_length=80, required=False, label=_("CTA label"))
    cta_href = blocks.CharBlock(max_length=255, required=False, label=_("CTA URL"))
    cta_page = blocks.PageChooserBlock(
        required=False,
        label=_("CTA page"),
        help_text=_("Pick an internal page instead of typing a CTA URL."),
    )
    featured = blocks.BooleanBlock(required=False, default=False, label=_("Featured"))
    tier = blocks.ChoiceBlock(
        choices=[
            ("outline", _("Outline — Community/open source")),
            ("default", _("Default — Standard/Solo")),
            ("featured", _("Featured — highlighted with accent")),
            ("managed", _("Managed — ribbon (hosted/Cloud)")),
        ],
        default="default",
        label=_("Visual tier"),
        help_text=_(
            "The card treatment: outline (Community), default (Standard/Solo), "
            "featured (Pro — accent + “most shipped”), managed (Cloud — ribbon)."
        ),
    )

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
    (e.g. LMS reusing Formints patterns).
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


class MediaGalleryBlock(blocks.StructBlock):
    """A visual gallery — screenshots, GIF walkthroughs and videos in a grid.

    Wraps multiple ``EditionPreviewImageBlock`` items into a single section
    with a display mode: grid (default), carousel (horizontal scroll with
    snap), or stack (full-bleed stack with lightbox). Used on product pages
    and edition previews to showcase multiple captures at once.

    The frontend GSAP layer animates gallery items on scroll in
    (scale+fade rise). The Django template renders the same grid with
    CSS-animated cards so the two render roads stay visually identical.
    """

    DISPLAY_CHOICES = [
        ("grid", _("Grid — responsive 2-3 column masonry")),
        ("carousel", _("Carousel — horizontal snap scroll")),
        ("stack", _("Stack — full-bleed with lightbox")),
    ]

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    display = blocks.ChoiceBlock(
        choices=DISPLAY_CHOICES,
        default="grid",
        label=_("Display mode"),
        help_text=_(
            "Grid shows a responsive 2-3 column layout. Carousel scrolls "
            "horizontally with snap points. Stack renders full-bleed images "
            "with a click-to-expand lightbox."
        ),
    )
    items = blocks.ListBlock(
        EditionPreviewImageBlock(),
        label=_("Gallery items"),
        help_text=_("Screenshots, GIFs and videos to display in the gallery."),
    )

    class Meta:
        icon = "image"
        label = _("Media gallery")
        template = "content/blocks/media_gallery.html"


class ComparisonRowBlock(blocks.StructBlock):
    """One feature row of the edition-comparison table.

    ``cells`` holds one value per column (in the same order as
    ``FeatureComparisonSectionBlock.columns``). The Django template renders
    ``Yes``/``No`` as check/cross glyphs and any other value as plain text
    (e.g. "60+ endpoints", "17 tables").
    """

    feature = blocks.CharBlock(max_length=200, label=_("Feature"))
    cells = blocks.ListBlock(
        blocks.CharBlock(max_length=120, label=_("Cell")),
        label=_("Values per column"),
        help_text=_("One value per edition column, in order: Yes / No / short note."),
    )

    class Meta:
        # No template: rows render inline inside feature_comparison.html so the
        # <tr> stays inside the table; a standalone template would fragment it.
        icon = "placeholder"
        label = _("Comparison row")


class FeatureComparisonSectionBlock(blocks.StructBlock):
    """Full feature-comparison table — edition columns vs capability rows.

    Used by product pages so buyers can compare editions row by row
    (e.g. Formints: Community · Standard · Pro · Cloud across ~26 rows).
    """

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    columns = blocks.ListBlock(
        blocks.CharBlock(max_length=40, label=_("Column")),
        label=_("Edition columns"),
        help_text=_("Edition names, left to right (e.g. Community, Standard, Pro, Cloud)."),
    )
    rows = blocks.ListBlock(ComparisonRowBlock(), label=_("Feature rows"))

    class Meta:
        icon = "list-ul"
        label = _("Feature comparison")
        template = "content/blocks/feature_comparison.html"


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
    topics = blocks.ListBlock(
        blocks.CharBlock(max_length=120, label=_("Topic")),
        label=_("Form topic choices"),
        required=False,
        help_text=_(
            "Options for the “What can we help with?” select — one per product "
            "or service line (e.g. Formints POS, Precis LMS, Loop CMS, "
            "Website building)."
        ),
    )

    class Meta:
        icon = "mail"
        label = _("Contact section")
        template = "content/blocks/contact_section.html"


class SocialLinkBlock(blocks.StructBlock):
    """A single social/profile link for a team member (label + url)."""

    platform = blocks.CharBlock(
        max_length=40, label=_("Platform"),
        help_text=_("e.g. GitHub, LinkedIn, Facebook, X."),
    )
    url = blocks.URLBlock(label=_("URL"))

    class Meta:
        icon = "link"
        label = _("Social link")
        template = "content/blocks/social_link.html"


class TeamMemberBlock(blocks.StructBlock):
    """A single team member card (name, role, bio, initials, social links)."""

    name = blocks.CharBlock(max_length=120, label=_("Name"))
    role = blocks.CharBlock(max_length=120, required=False, label=_("Role"))
    bio = blocks.TextBlock(required=False, label=_("Bio"))
    initials = blocks.CharBlock(
        max_length=4, required=False, label=_("Initials"),
        help_text=_("Avatar fallback, e.g. ME."),
    )
    links = blocks.ListBlock(SocialLinkBlock(), label=_("Links"), required=False)

    class Meta:
        icon = "user"
        label = _("Team member")
        template = "content/blocks/team_member.html"


class TeamSectionBlock(blocks.StructBlock):
    """Team grid — a heading plus member cards (About → Team subpage)."""

    eyebrow = blocks.CharBlock(max_length=80, required=False, label=_("Eyebrow"))
    title = blocks.CharBlock(max_length=200, label=_("Title"))
    description = blocks.TextBlock(required=False, label=_("Description"))
    members = blocks.ListBlock(TeamMemberBlock(), label=_("Members"))

    class Meta:
        icon = "group"
        label = _("Team section")
        template = "content/blocks/team.html"
