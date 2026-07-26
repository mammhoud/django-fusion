"""
Wagtail FusionPage models — page types wired to django-fusion layout system.

CMS-Fusion variant: uses purple theme palette via CSS custom properties.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class FusionPage(Page):
    """Abstract base page with fusion layout & render-first integration."""

    LAYOUT_CHOICES = [
        ("default", _("Default (Header + Content + Footer)")),
        ("full_width", _("Full Width (Edge-to-edge)")),
        ("sidebar", _("Sidebar (Content + Sidebar)")),
        ("blank", _("Blank (Content only)")),
    ]

    layout = models.CharField(
        max_length=20, choices=LAYOUT_CHOICES, default="default",
        help_text=_("Which fusion layout template to render this page with."),
    )
    fusion_render_first = models.BooleanField(
        default=False,
        help_text=_("Server-render HTML before Next.js hydration."),
    )
    fragment_name = models.CharField(
        max_length=255, blank=True, default="",
        help_text=_("Dotted fragment identifier. Auto-derived from slug if blank."),
    )
    show_in_nav = models.BooleanField(
        default=True,
        help_text=_("Include in navigation menus."),
    )
    custom_css = models.TextField(
        blank=True, default="",
        help_text=_("Optional inline CSS for this page only."),
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("layout"), FieldPanel("fusion_render_first"),
             FieldPanel("fragment_name"), FieldPanel("show_in_nav")],
            heading=_("Fusion Layout Settings"),
        ),
        FieldPanel("custom_css"),
    ]

    class Meta:
        abstract = True
        verbose_name = _("Fusion Page")

    @property
    def effective_fragment_name(self) -> str:
        if self.fragment_name:
            return self.fragment_name
        return f"pages.{self.slug.replace('-', '_')}"

    @property
    def effective_layout(self) -> str:
        return self.layout or "default"

    def get_context(self) -> dict:
        return {
            "page": self, "title": self.title, "page_title": self.title,
            "layout": self.effective_layout,
            "fragment_name": self.effective_fragment_name,
            "fusion_render_first": self.fusion_render_first,
            "show_in_nav": self.show_in_nav, "custom_css": self.custom_css,
            "seo_title": self.seo_title or self.title,
            "search_description": self.search_description or "",
        }


class FusionHomePage(FusionPage):
    """CMS Home page — root page with hero section."""

    hero_heading = models.CharField(
        max_length=255, blank=True, default="Welcome to Fusion CMS",
        help_text=_("Main hero heading."),
    )
    hero_subheading = models.TextField(
        blank=True, default="A modern content management platform powered by django-fusion and django-bolt.",
        help_text=_("Supporting text below the hero heading."),
    )

    content_panels = FusionPage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("hero_heading"), FieldPanel("hero_subheading")],
            heading=_("Home Page Hero"),
        ),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["pages.FusionContentPage"]

    class Meta:
        verbose_name = _("Fusion CMS Home Page")

    def get_context(self) -> dict:
        ctx = super().get_context()
        ctx.update({"hero_heading": self.hero_heading, "hero_subheading": self.hero_subheading})
        return ctx


class FusionContentPage(FusionPage):
    """Generic CMS content page."""

    body = RichTextField(
        blank=True, default="",
        features=["bold", "italic", "link", "h2", "h3", "h4", "ol", "ul", "image", "blockquote"],
        help_text=_("Main page content."),
    )
    featured_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text=_("Optional featured image."),
    )

    content_panels = FusionPage.content_panels + [
        FieldPanel("body"), FieldPanel("featured_image"),
    ]

    parent_page_types = ["pages.FusionHomePage", "pages.FusionContentPage"]
    subpage_types = ["pages.FusionContentPage"]

    class Meta:
        verbose_name = _("Fusion CMS Content Page")

    def get_context(self) -> dict:
        ctx = super().get_context()
        ctx.update({"body": self.body, "featured_image": self.featured_image})
        return ctx
