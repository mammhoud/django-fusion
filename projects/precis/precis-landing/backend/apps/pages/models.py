"""
Landing-fusion Wagtail page models.

Each page type carries the editable fields that drive the Astro frontend
sections (hero, stats, features, testimonials, pricing, faq, cta, contact).
Mirrors the structure of ``cms-fusion/backend/apps/content/models/pages/`` but
trimmed to the landing slice — see plan §5.1 / §5.3.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from apps.content.blocks import (
    ApplicationsSectionBlock,
    BadgesSectionBlock,
    BlogSectionBlock,
    BrandPaletteBlock,
    ContactSectionBlock,
    CtaBlock,
    EditionsSectionBlock,
    FaqSectionBlock,
    FeatureComparisonSectionBlock,
    FeaturesSectionBlock,
    HeroBlock,
    MediaGalleryBlock,
    PostVariantBlock,
    PricingSectionBlock,
    ProcessSectionBlock,
    ProductProfileBlock,
    ProjectBlock,
    ServicesSectionBlock,
    SnippetsSectionBlock,
    StatsSectionBlock,
    TeamSectionBlock,
    TechStackSectionBlock,
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
    badges = StreamField(
        [("badges", BadgesSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Badges & awards"),
        help_text=_(
            "A row of award/star/trust chips (stars, medals, seals, verified "
            "checks) shown under the section heading — social proof band."
        ),
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
        FieldPanel("badges", classname=SECTION_PANEL_CLASS),
        FieldPanel("pricing", classname=SECTION_PANEL_CLASS),
        FieldPanel("faq", classname=SECTION_PANEL_CLASS),
    ]


DISPLAY_MODE_CHOICES = [
    ("page", _("Full page")),
    ("modal", _("Modal only")),
    ("both", _("Page + modal")),
]


class DisplayModeMixin(models.Model):
    """
    Where a page is surfaced — as a full page, as a modal overlay, or both.

    Layers the *presentation* choice onto Wagtail's ``Page`` base model. The
    ``Page`` base already merges Wagtail's own base models (DraftStateMixin,
    RevisionMixin, PreviewableMixin, LockableMixin, SitemapMixin) — this mixin
    only adds the display-mode option on top, so any page type can opt in.

    Applied to ``BrandPage`` (which consumes it: the brand kit renders as
    its own /brand/ page and as a modal opened from product tooltips),
    ``ProductPage`` and ``TeamPage`` (which carry the option for future
    surfacing). The same admin panel and API field everywhere. Editors
    toggle ``display_mode`` in the Wagtail admin to pick page, modal, or
    both.
    """

    display_mode = models.CharField(
        max_length=10,
        choices=DISPLAY_MODE_CHOICES,
        default="both",
        verbose_name=_("Display mode"),
        help_text=_(
            "Where this page is surfaced: as its own full page (page), as a "
            "modal overlay triggered from product logos/tooltips (modal), or "
            "both. Modal-only hides the full-page affordance in the modal."
        ),
    )

    class Meta:
        abstract = True

    display_panels = [FieldPanel("display_mode")]


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


class TeamPage(DisplayModeMixin, LandingPage):
    """About → Team subpage — the people behind structa.cloud.

    A child of AboutPage, served at /about/team/. Carries a hero, a story
    body and the team grid (TeamSectionBlock) with member cards + social
    links, plus a CTA. The page is seeded with the founder + the product
    leads, each linking to their GitHub/LinkedIn/Facebook profiles.
    Carries ``display_mode`` (DisplayModeMixin) for future surfacing.
    """

    body_heading = _("Who builds this")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Team story content."),
    )
    team = StreamField(
        [("team", TeamSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Team"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Story"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("team"),
        *DisplayModeMixin.display_panels,
    ]

    template = "pages/team.html"

    class Meta:
        verbose_name = _("Team page")
        verbose_name_plural = _("Team pages")


class FounderPage(LandingPage):
    """About → Founder subpage — the engineer behind structa.cloud.

    A child of AboutPage, served at /about/founder/. Carries a hero, the
    engineer's story body, a tech-stack band (TechStackSectionBlock), a
    skills/values grid (FeaturesSectionBlock), plus a CTA — mirroring the
    Astro founder page so both render roads show the same document.
    """

    body_heading = _("The engineer")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("The founder's story — background, focus and working style."),
    )
    tech = StreamField(
        [("tech", TechStackSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Tech stack"),
    )
    features = StreamField(
        [("features", FeaturesSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Skills & values"),
        help_text=_("The capabilities and working principles the founder brings to every project."),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Story"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("tech"),
        FieldPanel("features"),
    ]

    template = "pages/founder.html"

    class Meta:
        verbose_name = _("Founder page")
        verbose_name_plural = _("Founder pages")


class StartupPage(LandingPage):
    """About → Startup subpage — the structa.cloud origin story.

    A child of AboutPage, served at /about/startup/. Carries a hero, the
    story body, a numbered timeline (ProcessSectionBlock — one step per
    era), a stats band, plus a CTA — mirroring the Astro startup page.
    """

    body_heading = _("The story")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("How structa.cloud grew from freelance projects into a monorepo of products."),
    )
    process = StreamField(
        [("process", ProcessSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Timeline"),
        help_text=_("One numbered step per era — the build-as-you-go story rendered as a process band."),
    )
    stats = StreamField(
        [("stats", StatsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Stats"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Story"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("process"),
        FieldPanel("stats"),
    ]

    template = "pages/startup.html"

    class Meta:
        verbose_name = _("Startup page")
        verbose_name_plural = _("Startup pages")

class BrandPage(DisplayModeMixin, LandingPage):
    """Brand kit page — the identity system for every product.

    Renders ``pages/brand.html``: one identity board per live product (lockup,
    construction, essence, colour system, voice), derived from the catalog
    cards + BRAND_SPEC so it can never drift from the products it describes.

    ``display_mode`` (from DisplayModeMixin) decides whether the brand kit is
    reachable as a full page, as a modal opened from product tooltips, or both
    — the default is both.

    ``palette_overrides`` lets editors replace the hardcoded system swatches
    per product with their own hex palette (see get_palette_overrides).
    """

    palette_overrides = StreamField(
        [("palette", BrandPaletteBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Palette overrides"),
        help_text=_(
            "One block per product: pick the product and enter up to 5 hex "
            "swatches (accent first). An override replaces that product's "
            "default system palette on the /brand/ page and in the brand "
            "modal; products without an override keep the hardcoded BRAND_SPEC "
            "palette."
        ),
    )

    template = "pages/brand.html"
    max_count = 1

    content_panels = LandingPage.content_panels + [
        FieldPanel("palette_overrides"),
        *DisplayModeMixin.display_panels,
    ]

    class Meta:
        verbose_name = _("Brand page")
        verbose_name_plural = _("Brand pages")

    def get_palette_overrides(self) -> dict[str, list[str]]:
        """Palette overrides keyed by product slug — ``{slug: [hex, …]}``.

        Resolves each BrandPaletteBlock's PageChooser to the product's slug
        and returns its hex swatches. Products without a block (or with an
        empty swatch list) are absent, so callers fall back to BRAND_SPEC.
        Only ``#RRGGBB`` values pass: every road (backend boards + the page
        API) consumes this method, so malformed or non-hex input can never
        reach the inline ``background:`` styles rendered on the brand page.
        """
        import re

        hex_re = re.compile(r"^#[0-9a-fA-F]{6}$")
        overrides: dict[str, list[str]] = {}
        if not self.palette_overrides:
            return overrides
        for block in self.palette_overrides:
            if block.block_type != "palette":
                continue
            value = block.value
            product = value.get("product")
            slug = getattr(product, "slug", None)
            swatches = [
                str(c).strip()
                for c in (value.get("swatches") or [])
                if hex_re.match(str(c).strip())
            ]
            if slug and swatches:
                overrides[slug] = swatches
        return overrides


class ServicesPage(LandingPage):
    """Services page — hero, offering grid (features), and the 'build as you go' process."""

    body_heading = _("What we do")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Services, offering and approach content."),
    )
    services = StreamField(
        [("services", ServicesSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Services"),
    )
    process = StreamField(
        [("process", ProcessSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Build as you go"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Content"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("services"),
        FieldPanel("process"),
    ]

    template = "pages/services.html"

    class Meta:
        verbose_name = _("Services page")
        verbose_name_plural = _("Services pages")


class ShowInNavMixin(models.Model):
    """Shared nav-control fields for page types (matches migration 0004).

    ``show_in_nav``/``nav_order`` let editors toggle a page in the header nav
    and set its position. The main nav source of truth is ``LandingModule``
    (apps/core/site.py); these fields are used by the Wagtail-tree nav
    fallback and exposed on the page API.
    """

    show_in_nav = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Include this page in the main site header navigation."),
        verbose_name=_("Show in navigation"),
    )
    nav_order = models.IntegerField(
        default=100,
        help_text=_("Lower numbers appear first in the header nav."),
        verbose_name=_("Navigation order"),
    )

    class Meta:
        abstract = True

    nav_panels = [FieldPanel("show_in_nav"), FieldPanel("nav_order")]


PHASE_KIND_CHOICES = [
    ("discovery", _("Discovery")),
    ("build", _("Build")),
    ("launch", _("Launch")),
    ("enhance", _("Enhance")),
]


class PhasePage(LandingPage):
    """A Wagtail-managed delivery phase beneath the Services page.

    Phases are deliberate content documents rather than hardcoded cards. Each
    phase can own PromptPage children, so editors can publish a practical
    prompt library alongside the service methodology.
    """

    phase_number = models.PositiveIntegerField(default=1, verbose_name=_("Phase number"))
    phase_label = models.CharField(
        max_length=20,
        choices=PHASE_KIND_CHOICES,
        default="discovery",
        verbose_name=_("Phase type"),
    )
    body = RichTextField(blank=True, verbose_name=_("Phase brief"))
    outcomes = models.TextField(
        blank=True,
        help_text=_("One outcome per line, shown as the phase checklist."),
        verbose_name=_("Outcomes"),
    )

    parent_page_types = ["pages.ServicesPage"]
    subpage_types = ["pages.PromptPage"]
    template = "pages/phase.html"

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("phase_number"), FieldPanel("phase_label")],
            heading=_("Phase identity"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("body"),
        FieldPanel("outcomes"),
    ]

    class Meta:
        verbose_name = _("Delivery phase")
        verbose_name_plural = _("Delivery phases")


class PromptPage(LandingPage):
    """A reusable brief/prompt document owned by a PhasePage."""

    prompt = models.TextField(verbose_name=_("Prompt"))
    context = RichTextField(blank=True, verbose_name=_("Context"))
    output = RichTextField(blank=True, verbose_name=_("Expected output"))
    tool = models.CharField(
        max_length=80,
        blank=True,
        help_text=_("Optional tool or stack label, for example Astro + Wagtail."),
        verbose_name=_("Tool / stack"),
    )

    parent_page_types = ["pages.PhasePage"]
    subpage_types = []
    template = "pages/prompt.html"

    content_panels = LandingPage.content_panels + [
        FieldPanel("prompt"),
        FieldPanel("context"),
        FieldPanel("output"),
        FieldPanel("tool"),
    ]

    class Meta:
        verbose_name = _("Implementation prompt")
        verbose_name_plural = _("Implementation prompts")


class PricingPage(ShowInNavMixin, LandingPage):
    """Dedicated pricing page — hero, per-product pricing tabs, faq, cta.

    The tabbed view (Formints · Precis LMS · Loop · Syntara · vResume) is
    driven by ``get_product_pricing()`` — every live, non-hidden product's
    editions — plus an optional editor-authored ``pricing`` fallback stack.
    """

    def get_product_pricing(self) -> list[dict]:
        """All live, non-hidden products with their editions, for pricing tabs."""
        from apps.pages.models import ProductsPage as _ProductsPage

        products_page = _ProductsPage.objects.first()
        if products_page is None:
            return []
        result = []
        for child in products_page.get_children().live():
            specific = child.specific
            if isinstance(specific, ProductPage) and not specific.hidden:
                result.append(
                    {
                        "slug": specific.slug,
                        "title": specific.title,
                        "tagline": specific.tagline,
                        "version": specific.version,
                        "logo_style": specific.logo_style,
                        "status": specific.status,
                        "display_mode": specific.display_mode,
                        "href": f"/products/{specific.slug}/",
                        "editions": specific.get_editions(),
                    }
                )
        return result

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
        FieldPanel("pricing"),
        FieldPanel("faq"),
        *ShowInNavMixin.nav_panels,
    ]

    template = "pages/pricing.html"

    class Meta:
        verbose_name = _("Pricing page")
        verbose_name_plural = _("Pricing pages")


class BlogPage(ShowInNavMixin, LandingPage):
    """Blog index — hero, post grid, cta."""

    blog = StreamField(
        [("blog", BlogSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Blog"),
    )

    content_panels = LandingPage.content_panels + [
        FieldPanel("blog"),
        *ShowInNavMixin.nav_panels,
    ]

    template = "pages/blog.html"

    class Meta:
        verbose_name = _("Blog page")
        verbose_name_plural = _("Blog pages")



class BlogPostPage(ShowInNavMixin, LandingPage):
    """A single blog post — child of the Blog index, served at /blog/<slug>/.

    Carries the post meta (category, date, read time), an excerpt used by the
    index grid, and a RichText body for the detail page. Slugs must match the
    ``slug`` field of the matching ``BlogPostBlock`` on the Blog index so grid
    cards link to live pages.
    """

    body_heading = _("The post")

    category = models.CharField(
        max_length=80,
        blank=True,
        verbose_name=_("Category"),
    )
    post_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date"),
    )
    read_time = models.CharField(
        max_length=40,
        blank=True,
        verbose_name=_("Read time"),
        help_text=_("e.g. 6 min read"),
    )
    excerpt = models.TextField(
        blank=True,
        verbose_name=_("Excerpt"),
        help_text=_("One-liner shown on the blog index grid card."),
    )
    hero_screenshot_url = models.URLField(
        blank=True,
        verbose_name=_("Hero screenshot URL"),
        help_text=_(
            "Optional image shown under the post hero (e.g. a product "
            "screenshot). Leave empty for a text-only post."
        ),
    )
    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("The post content — paragraphs, headings, lists, code."),
    )
    variants = StreamField(
        [("variant", PostVariantBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Variants & screenshots"),
        help_text=_(
            "Screenshot variants of the product — each with an optional image, "
            "caption and hyperlink (e.g. the Community terminal linking to its "
            "edition preview)."
        ),
    )
    snippets = StreamField(
        [("snippets", SnippetsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Code sections"),
        help_text=_(
            "Code for this post's engineering deep dive. Keep implementation "
            "sections on BlogPostPage records, not product or catalog pages."
        ),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("post_date"),
                FieldPanel("read_time"),
                FieldPanel("excerpt"),
            ],
            heading=_("Post meta"),
            classname=SECTION_PANEL_CLASS,
        ),
        MultiFieldPanel(
            [FieldPanel("hero_screenshot_url")],
            heading=_("Hero screenshot"),
            classname=SECTION_PANEL_CLASS,
        ),
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Body"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("variants"),
        FieldPanel("snippets"),
        *ShowInNavMixin.nav_panels,
    ]

    template = "pages/blog_post.html"

    class Meta:
        verbose_name = _("Blog post page")
        verbose_name_plural = _("Blog post pages")

    @property
    def is_blog_post(self) -> bool:
        """True — lets the shared content partial gate blog-only sections
        (hero screenshot, variants, comments) without Django-template
        ``__class__`` access (which templates cannot resolve)."""
        return True

    def get_approved_comments(self):
        """Approved comments for this post, oldest first.

        The single source of approved comments used by the server-rendered
        comment section and the public GET comments API — moderation lives on
        ``PostComment.is_approved`` in the Wagtail admin.
        """
        from apps.content.models.comments import PostComment

        return (
            PostComment.objects.filter(post=self, is_approved=True)
            .select_related("author")
            .order_by("created_at")
        )

PRODUCT_CATEGORY_CHOICES = [
    ("application", _("Application")),
    ("platform", _("Platform")),
    ("library", _("Library")),
]

PRODUCT_LOGO_CHOICES = [
    ("crest", _("Crest — Formints merchant seal")),
    ("ribbon", _("Ribbon — Precis LMS award ribbon")),
    ("isometric", _("Isometric — Loop blocks")),
    ("orbit", _("Orbit — Syntara AI signal")),
    ("ascent", _("Ascent — vResume career path")),
    ("research", _("Research signal — CTC Research evidence path")),
]

PRODUCT_STATUS_CHOICES = [
    ("live", _("Live / released")),
    ("development", _("Under development")),
]


class ProductPage(ShowInNavMixin, DisplayModeMixin, LandingPage):
    """
    A single product page — the reference document for one product.

    Carries everything another project needs to reuse it (e.g. LMS reusing
    Formints patterns): an overview, its tech stack, its editions with
    per-edition pricing, preview captures, features, FAQ and CTA.    A legacy ``snippets`` column remains on the model for migration
    compatibility, but code is owned by BlogPostPage deep dives and is not
    editable or rendered on product pages.
    These pages live as children of ``ProductsPage`` and are listed there.
    Carries ``display_mode`` (DisplayModeMixin) for future surfacing.
    """

    category = models.CharField(
        max_length=20,
        choices=PRODUCT_CATEGORY_CHOICES,
        default="application",
        verbose_name=_("Category"),
        help_text=_(
            "How the product is positioned in the catalog: an Application "
            "(desktop/web app), a Platform (hosted service), or a Library "
            "(reusable open-source package)."
        ),
    )
    tagline = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Tagline"),
        help_text=_("One-line summary shown on the product card in the /products/ listing."),
    )
    version = models.CharField(
        max_length=40,
        blank=True,
        verbose_name=_("Product version"),
        help_text=_("Release label shown on catalog and product detail pages, for example beta 0.2 or v2.7."),
    )
    logo_style = models.CharField(
        max_length=20,
        choices=PRODUCT_LOGO_CHOICES,
        default="crest",
        verbose_name=_("Logo"),
        help_text=_(
            "The brand mark shown on the product card and detail page — each "
            "mark is a constructed symbol tied to the product: crest (Formints "
            "merchant seal), ribbon (Precis LMS award ribbon), isometric (Loop "
            "blocks), orbit (Syntara AI signal), or ascent (vResume career path)."
        ),
    )
    status = models.CharField(
        max_length=20,
        choices=PRODUCT_STATUS_CHOICES,
        default="live",
        verbose_name=_("Status"),
        help_text=(
            "Set to “Under development” to show the amber caution badge + "
            "warning banner. CAUTION: development products are previews — "
            "their APIs, editions and pricing may change before release."
        ),
    )
    hidden = models.BooleanField(
        default=False,
        verbose_name=_("Hidden from catalog"),
        help_text=_(
            "Hide this product from the /products/ listing and pricing tabs "
            "while keeping its detail page reachable by direct link "
            "(e.g. internal libraries like ceptor-ai)."
        ),
    )
    show_on_home = models.BooleanField(
        default=True,
        verbose_name=_("Show on home"),
        help_text=_(
            "Show this product in the home preview grid. Turn off for "
            "subproducts (e.g. vResume) that stay catalog-only: they still "
            "appear on /products/ and the pricing tabs, just not on the "
            "homepage cards."
        ),
    )
    body = RichTextField(
        blank=True,
        verbose_name=_("Overview"),
        help_text=_("What this product is and why it exists."),
    )
    tech = StreamField(
        [("tech", TechStackSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Tech stack"),
    )
    editions = StreamField(
        [("editions", EditionsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Editions & pricing"),
    )
    # Retained as a compatibility column for old revisions. New code belongs
    # exclusively to BlogPostPage.snippets and this field is intentionally not
    # exposed in ProductPage.content_panels.
    snippets = StreamField(
        [("snippets", SnippetsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Legacy reference snippets"),
        help_text=_("Legacy data only; author code on a BlogPostPage deep dive."),
    )
    comparison = StreamField(
        [("comparison", FeatureComparisonSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Feature comparison"),
        help_text=_(
            "A full edition-by-edition capability table (columns = editions, "
            "rows = features). Cells use Yes / No / short notes."
        ),
    )
    applications = StreamField(
        [("applications", ApplicationsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Built with this product"),
        help_text=_(
            "Real application/sites running on this product (e.g. Loop "
            "listing vResume + this site). One card each, linking out to the "
            "running product or its edition preview."
        ),
    )
    features = StreamField(
        [("features", FeaturesSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Features"),
    )
    gallery = StreamField(
        [("gallery", MediaGalleryBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Media gallery"),
        help_text=_("Visual gallery: screenshots, GIFs and videos in a grid, carousel or stack."),
    )
    profile = StreamField(
        [("profile", ProductProfileBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Product profile"),
        help_text=_(
            "The business profile: ideal customer profiles (who + behaviour), "
            "capacity & scale, financial/supply-chain reporting, channels & "
            "loyalty, and the product's distinct marketing tone."
        ),
    )
    faq = StreamField(
        [("faq", FaqSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("FAQ"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("tagline"),
                FieldPanel("version"),
                FieldPanel("logo_style"),
                FieldPanel("status"),
                FieldPanel("hidden"),
                FieldPanel("show_on_home"),
            ],
            heading=_("Listing card"),
            classname=SECTION_PANEL_CLASS,
        ),
        MultiFieldPanel(
            [FieldPanel("body")],
            heading=_("Overview"),
            classname=SECTION_PANEL_CLASS,
        ),
        FieldPanel("tech"),
        FieldPanel("editions"),
        FieldPanel("comparison"),
        FieldPanel("applications"),
        # Reference snippets are legacy data retained for compatibility. Code
        # is authored and rendered only on BlogPostPage deep dives; keeping
        # this field out of the product editor prevents new product code
        # sections from being created accidentally.
        FieldPanel("features"),
        FieldPanel("gallery"),
        FieldPanel("profile"),
        FieldPanel("faq"),
        *ShowInNavMixin.nav_panels,
        *DisplayModeMixin.display_panels,
    ]

    template = "pages/product.html"

    class Meta:
        verbose_name = _("Product page")
        verbose_name_plural = _("Product pages")

    def clean(self):
        """Keep the legacy field empty: code belongs to blog deep dives only."""
        super().clean()
        if self.snippets:
            raise ValidationError(
                {"snippets": _("Code sections are authored only on blog posts.")}
            )

    def _resolve_edition_cta(self, edition) -> dict:
        """Flatten one edition card for JSON/API consumers (CTA resolved).

        A chosen ``cta_page`` wins over the manual ``cta_href`` and fills an
        empty ``cta_label`` (the button's visible header) — matching the
        ButtonBlock resolution on the page API. Values are JSON-safe.
        """
        from wagtail.models import Page as WagtailPage

        cta_page = edition.get("cta_page")
        cta_href = edition.get("cta_href", "")
        cta_label = edition.get("cta_label", "")
        if isinstance(cta_page, WagtailPage):
            # Resolve the URL first so an unresolvable page leaves the manual
            # href/label untouched (no partial state) instead of falling into
            # a broad except.
            page_url = cta_page.url or ""
            if page_url:
                cta_href = cta_href or page_url
                cta_label = cta_label or cta_page.title
                cta_page = {"id": cta_page.pk, "title": cta_page.title, "url": page_url}
            else:
                cta_page = None
        else:
            cta_page = None
        from django.utils.text import slugify

        preview_images = []
        for image in edition.get("preview_images", []):
            # StructValue and plain dict are both used here: the former comes
            # from Wagtail's editor, the latter from seeded JSON/tests.
            url = image.get("url", "") if hasattr(image, "get") else ""
            if not url:
                continue
            kind = image.get("kind", "image") if hasattr(image, "get") else "image"
            poster = image.get("poster", "") if hasattr(image, "get") else ""
            label = image.get("label", "") if hasattr(image, "get") else ""
            alt = image.get("alt", "") if hasattr(image, "get") else ""
            normalized_url = str(url)
            if normalized_url.startswith("previews/"):
                normalized_url = f"/static/{normalized_url}"
            normalized_poster = str(poster)
            if normalized_poster.startswith("previews/"):
                normalized_poster = f"/static/{normalized_poster}"
            preview_images.append(
                {
                    "url": normalized_url,
                    "kind": str(kind) if str(kind) in {"image", "gif", "video"} else "image",
                    "poster": normalized_poster,
                    "label": str(label),
                    "alt": str(alt) or str(label) or "Edition preview",
                }
            )
        return {
            "name": edition.get("name", ""),
            "price": edition.get("price", ""),
            "period": edition.get("period", ""),
            "tagline": edition.get("tagline", ""),
            "features": list(edition.get("features", [])),
            "preview_images": preview_images,
            "preview_href": f"/products/{self.slug}/preview/{slugify(str(edition.get('name', '')))}/",
            "tier": edition.get("tier", "default"),
            "featured": bool(edition.get("featured", False)),
            "offer_label": edition.get("offer_label", ""),
            "offer_old_price": edition.get("offer_old_price", ""),
            "cta_label": cta_label,
            "cta_href": cta_href,
            "cta_page": cta_page,
        }

    def get_editions(self) -> list[dict]:
        """The edition list (name, price, period, tier, tagline, featured, CTA)
        from the editions StreamField, flattened for cards + pricing tabs."""
        if not self.editions:
            return []
        for block in self.editions:
            if block.block_type == "editions":
                return [self._resolve_edition_cta(e) for e in block.value.get("editions", [])]
        return []

    def get_edition(self, name: str) -> dict | None:
        """The full edition dict (features + CTA included) by name.

        Edition names are matched case-insensitively ("Community", "community")
        so preview URLs like /products/formint-pos/preview/community/ resolve.
        Returns None when no edition matches.
        """
        if not self.editions:
            return None
        from django.utils.text import slugify

        target = slugify(name)
        for block in self.editions:
            if block.block_type == "editions":
                for edition in block.value.get("editions", []):
                    if slugify(str(edition.get("name", ""))) == target:
                        data = self._resolve_edition_cta(edition)
                        # Features are CharBlocks — already plain strings.
                        data["features"] = list(edition.get("features", []))
                        return data
        return None

    def get_preview_gallery(self) -> list[dict]:
        """Collect the product's edition captures for the detail-page gallery.

        Edition previews remain the editorial source of truth. The detail page
        gets one deduplicated gallery, while edition preview routes keep their
        own focused galleries. Prefixing labels with the edition keeps a mixed
        product gallery understandable without adding another content field.
        """
        gallery: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for edition in self.get_editions():
            edition_name = str(edition.get("name", "")).strip()
            for media in edition.get("preview_images", []):
                url = str(media.get("url", "")).strip()
                if not url:
                    continue
                kind = str(media.get("kind", "image"))
                identity = (url, kind)
                if identity in seen:
                    continue
                seen.add(identity)
                label = str(media.get("label", "")).strip()
                gallery.append(
                    {
                        "url": url,
                        "kind": kind,
                        "poster": str(media.get("poster", "")),
                        "label": f"{edition_name} · {label}" if label else edition_name,
                        "alt": str(media.get("alt", "")) or f"{edition_name} product preview",
                        "edition": edition_name,
                    }
                )
        return gallery

    def get_product_card(self) -> dict:
        """The listing-card payload for the /products/ page + API.

        Carries enough detail for the catalog listing to render rich cards
        without a second round-trip: category, logo, status, edition names +
        prices + tiers, tech tags, and a plain-text excerpt of the overview.
        When a matching ``Product`` snippet exists (by slug), its language +
        unified currency + base price enrich the card so the catalog carries
        the same language/currency contract as courses.
        """
        editions: list[dict] = self.get_editions()
        tech: list[str] = []
        if self.tech:
            for block in self.tech:
                if block.block_type == "tech":
                    tech = [str(i) for i in block.value.get("items", [])]
                    break
        try:
            from apps.content.models.products import Product, default_currency

            snippet = Product.objects.filter(slug=self.slug, is_published=True).first()
        except Exception:
            snippet = None
        card = {
            "title": self.title,
            "slug": self.slug,
            "tagline": self.tagline,
            "version": self.version,
            "href": f"/products/{self.slug}/",
            "category": self.get_category_display().lower(),
            "logo_style": self.logo_style,
            "status": self.status,
            "display_mode": self.display_mode,
            "editions": editions,
            "tech": tech,
            "excerpt": self._overview_excerpt(),
            "language": snippet.language if snippet else "en",
            "currency": (snippet.currency or default_currency()) if snippet else default_currency(),
            "price": str(snippet.price) if snippet else (editions[0].get("price", "0") if editions else "0"),
        }
        return card

    def _overview_excerpt(self, limit: int = 150) -> str:
        """First ~150 plain-text characters of the overview body (for cards)."""
        import html
        import re

        if not self.body:
            return ""
        text = re.sub(r"<[^>]+>", " ", str(self.body))
        text = html.unescape(text)  # RichText entities → plain characters
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= limit:
            return text
        return text[: limit - 1].rstrip() + "…"


class ProductsPage(SectionStackMixin, LandingPage):
    """Products page — the full product document: hero, lines, projects (cards),
    stats, features, pricing, testimonials, faq, cta."""

    body_heading = _("What ships with Fusion")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Product lines and highlights content."),
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

    template = "pages/products.html"

    class Meta:
        verbose_name = _("Products page")
        verbose_name_plural = _("Products pages")

    def get_product_cards(self, for_home: bool = False) -> list[dict]:
        """Product cards — one per live, non-hidden ProductPage child.

        ``for_home=True`` filters to products flagged ``show_on_home`` so the
        homepage preview grid stays curated (subproducts like vResume remain
        catalog-only). The full catalog (``/products/``, pricing tabs) always
        lists every live, non-hidden product.
        """
        from apps.pages.models import ProductPage as _ProductPage

        return [
            child.specific.get_product_card()
            for child in self.get_children().live()
            if isinstance(child.specific, _ProductPage)
            and not child.specific.hidden
            and (not for_home or child.specific.show_on_home)
        ]


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
