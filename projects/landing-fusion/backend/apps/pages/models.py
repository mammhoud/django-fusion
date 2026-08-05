"""
Landing-fusion Wagtail page models.

Each page type carries the editable fields that drive the Astro frontend
sections (hero, stats, features, testimonials, pricing, faq, cta, contact).
Mirrors the structure of ``cms-fusion/backend/apps/content/models/pages/`` but
trimmed to the landing slice — see plan §5.1 / §5.3.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from apps.content.blocks import (
    BlogSectionBlock,
    ContactSectionBlock,
    CtaBlock,
    EditionsSectionBlock,
    FaqSectionBlock,
    FeaturesSectionBlock,
    HeroBlock,
    PricingSectionBlock,
    ProcessSectionBlock,
    ProjectBlock,
    ServicesSectionBlock,
    SnippetsSectionBlock,
    StatsSectionBlock,
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
        FieldPanel("pricing", classname=SECTION_PANEL_CLASS),
        FieldPanel("faq", classname=SECTION_PANEL_CLASS),
    ]


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
    and set its position. The main nav source of truth is ``LandingSite``
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


class PricingPage(ShowInNavMixin, LandingPage):
    """Dedicated pricing page — hero, pricing tiers, faq, cta."""

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
    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("The post content — paragraphs, headings, lists, code."),
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
            [FieldPanel("body")],
            heading=_("Body"),
            classname=SECTION_PANEL_CLASS,
        ),
        *ShowInNavMixin.nav_panels,
    ]

    template = "pages/blog_post.html"

    class Meta:
        verbose_name = _("Blog post page")
        verbose_name_plural = _("Blog post pages")

class ProductPage(ShowInNavMixin, LandingPage):
    """
    A single product page — the reference document for one product.

    Carries everything another project needs to reuse it (e.g. LMS reusing
    Forge POS patterns): an overview, its tech stack, its editions with
    per-edition pricing, reference snippets/models, features, FAQ and CTA.
    These pages live as children of ``ProductsPage`` and are listed there.
    """

    tagline = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Tagline"),
        help_text=_("One-line summary shown on the product card in the /products/ listing."),
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
    snippets = StreamField(
        [("snippets", SnippetsSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Reference snippets"),
    )
    features = StreamField(
        [("features", FeaturesSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Features"),
    )
    faq = StreamField(
        [("faq", FaqSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("FAQ"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("tagline")],
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
        FieldPanel("snippets"),
        FieldPanel("features"),
        FieldPanel("faq"),
        *ShowInNavMixin.nav_panels,
    ]

    template = "pages/product.html"

    class Meta:
        verbose_name = _("Product page")
        verbose_name_plural = _("Product pages")

    def get_product_card(self) -> dict:
        """The listing-card payload for the /products/ page + API."""
        return {
            "title": self.title,
            "slug": self.slug,
            "tagline": self.tagline,
            "href": f"/products/{self.slug}/",
        }


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

    def get_product_cards(self) -> list[dict]:
        """Product cards — one per live ProductPage child, for the listing + API."""
        from apps.pages.models import ProductPage as _ProductPage

        return [
            child.specific.get_product_card()
            for child in self.get_children().live()
            if isinstance(child.specific, _ProductPage)
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


class ProjectsPage(SectionStackMixin, LandingPage):
    """
    Projects page — the full project document: hero, body, the repo's project cards
    (with editions and shared/standalone features), then the shared section stack.
    """

    body_heading = _("Built from this monorepo")
    projects_heading = _("Projects in this repo")

    body = RichTextField(
        blank=True,
        verbose_name=_("Body"),
        help_text=_("Intro text above the project cards."),
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

    template = "pages/projects.html"

    class Meta:
        verbose_name = _("Projects page")
        verbose_name_plural = _("Projects pages")


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
