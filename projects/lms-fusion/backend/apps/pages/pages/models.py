"""
Wagtail FusionPage models — page types wired to django-fusion layout system.

Each page type stores fusion-specific metadata (layout choice, render-first
preference, fragment name) that is consumed by companion ``RoutableComponent``
views and the ``{% fusion_layout %}`` template tag.

Usage::

    from apps.pages.pages.models import FusionHomePage, FusionContentPage

    # Create in Wagtail admin or programmatically:
    home = FusionHomePage(title="Welcome", layout="full_width", fusion_render_first=True)
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class FusionPage(Page):
    """
    Abstract base page with fusion layout & render-first integration.

    Fields added to every Fusion page:
        - layout: which fusion layout template to use
        - fusion_render_first: server-render HTML before Next.js hydration
        - fragment_name: custom fragment identifier (auto-derived from slug if blank)
        - show_in_nav: include in navigation menus
        - custom_css: optional inline CSS for page-specific overrides
    """

    LAYOUT_CHOICES = [
        ("default", _("Default (Header + Content + Footer)")),
        ("full_width", _("Full Width (No sidebar, edge-to-edge)")),
        ("sidebar", _("Sidebar (Content + Sidebar)")),
        ("blank", _("Blank (Content only, no chrome)")),
    ]

    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default="default",
        help_text=_("Which fusion layout template to render this page with."),
    )

    fusion_render_first = models.BooleanField(
        default=False,
        help_text=_(
            "When enabled, Django renders the full HTML server-side before "
            "Next.js hydration. The frontend FusionProxy detects this and "
            "injects the HTML directly instead of fetching JSON."
        ),
    )

    fragment_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_(
            "Dotted fragment identifier (e.g. 'pages.about'). "
            "Auto-derived from the slug if left blank."
        ),
    )

    show_in_nav = models.BooleanField(
        default=True,
        help_text=_("Include this page in the main navigation menu."),
    )

    custom_css = models.TextField(
        blank=True,
        default="",
        help_text=_("Optional inline CSS applied only to this page."),
    )

    # ── Content panels ──────────────────────────────────────────────

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("layout"),
                FieldPanel("fusion_render_first"),
                FieldPanel("fragment_name"),
                FieldPanel("show_in_nav"),
            ],
            heading=_("Fusion Layout Settings"),
        ),
        FieldPanel("custom_css"),
    ]

    class Meta:
        abstract = True
        verbose_name = _("Fusion Page")
        verbose_name_plural = _("Fusion Pages")

    # ── Properties used by companion RoutableComponent views ────────

    @property
    def effective_fragment_name(self) -> str:
        """Return the fragment name, deriving from slug if blank."""
        if self.fragment_name:
            return self.fragment_name
        return f"pages.{self.slug.replace('-', '_')}"

    @property
    def effective_layout(self) -> str:
        """Return the layout name, defaulting to 'default'."""
        return self.layout or "default"

    def get_context(self) -> dict:
        """Return a context dict for template rendering."""
        return {
            "page": self,
            "title": self.title,
            "page_title": self.title,
            "layout": self.effective_layout,
            "fragment_name": self.effective_fragment_name,
            "fusion_render_first": self.fusion_render_first,
            "show_in_nav": self.show_in_nav,
            "custom_css": self.custom_css,
            "seo_title": self.seo_title or self.title,
            "search_description": self.search_description or "",
        }


class FusionHomePage(FusionPage):
    """
    Home page — only allowed at the root of the site tree.

    Uses the 'full_width' layout by default for maximum visual impact.
    """

    hero_heading = models.CharField(
        max_length=255,
        blank=True,
        default="Welcome to Fusion",
        help_text=_("Main hero heading displayed on the home page."),
    )

    hero_subheading = models.TextField(
        blank=True,
        default="A modern platform powered by django-fusion and django-bolt.",
        help_text=_("Supporting text below the hero heading."),
    )

    content_panels = FusionPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_heading"),
                FieldPanel("hero_subheading"),
            ],
            heading=_("Home Page Hero"),
        ),
    ]

    # Only allowed at root
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["fusion_pages.FusionContentPage"]

    class Meta:
        verbose_name = _("Fusion Home Page")
        verbose_name_plural = _("Fusion Home Pages")

    def get_context(self) -> dict:
        ctx = super().get_context()
        ctx.update(
            {
                "hero_heading": self.hero_heading,
                "hero_subheading": self.hero_subheading,
            }
        )
        return ctx


class FusionContentPage(FusionPage):
    """
    Generic content page — can be placed anywhere in the page tree.

    Supports RichTextField for body content and an optional featured image.
    """

    body = RichTextField(
        blank=True,
        default="",
        features=["bold", "italic", "link", "h2", "h3", "h4", "ol", "ul", "image", "blockquote"],
        help_text=_("Main page content."),
    )

    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Optional featured image for the page header."),
    )

    content_panels = FusionPage.content_panels + [
        FieldPanel("body"),
        FieldPanel("featured_image"),
    ]

    # Can be child of HomePage or another ContentPage
    parent_page_types = ["fusion_pages.FusionHomePage", "fusion_pages.FusionContentPage"]
    subpage_types = ["fusion_pages.FusionContentPage"]

    class Meta:
        verbose_name = _("Fusion Content Page")
        verbose_name_plural = _("Fusion Content Pages")

    def get_context(self) -> dict:
        ctx = super().get_context()
        ctx.update(
            {
                "body": self.body,
                "featured_image": self.featured_image,
            }
        )
        return ctx
