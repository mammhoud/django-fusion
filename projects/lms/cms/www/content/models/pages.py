"""
Wagtail CMS Page models for dynamic frontend content.

These replace the hardcoded STATIC_PAGES dict in plugins/pages/content.py.
Each page type uses StreamField blocks from www.content.models.blocks so
that content editors can build pages through the Wagtail admin panel.

All pages support Wagtail i18n translation via ``WAGTAIL_I18N_ENABLED``.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.rich_text import RichText

from www.content.models.blocks import PAGE_CONTENT_BLOCKS


# ═══════════════════════════════════════════════════════════════════
# Page mixin — shared fields for SEO and content blocks
# ═══════════════════════════════════════════════════════════════════

class ContentPageMixin(models.Model):
    """Abstract base for all CMS-backed content pages.

    Inherits ``models.Model`` so Django's metaclass registers
    ``seo_description`` and ``last_updated`` as real model fields.
    ``seo_title`` is intentionally NOT defined here — Wagtail's
    ``Page`` model already provides it.

    The ``abstract = True`` Meta flag prevents Django from
    creating a separate DB table.
    """

    seo_description = models.TextField(
        blank=True, default="",
        help_text=_("Meta description for search engines."),
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = "content"

    @property
    def seo_dict(self) -> dict:
        return {
            "title": self.seo_title or self.title,
            "description": self.seo_description or "",
        }

    @property
    def page_slug(self) -> str:
        """Return the normalized slug (e.g., 'about-us')."""
        return self.slug


# ═══════════════════════════════════════════════════════════════════
# Home Page
# ═══════════════════════════════════════════════════════════════════

class DynamicHomePage(ContentPageMixin, Page):
    """Site home page — hero, stats, featured sections, CTA."""

    body = StreamField(PAGE_CONTENT_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("seo_title"), FieldPanel("seo_description")],
            heading=_("SEO"),
        ),
        FieldPanel("body"),
    ]

    subpage_types = []

    class Meta:
        db_table = "content_dynamic_homepage"
        verbose_name = _("home page")
        verbose_name_plural = _("home pages")
        app_label = "content"


# ═══════════════════════════════════════════════════════════════════
# About Page
# ═══════════════════════════════════════════════════════════════════

class DynamicAboutPage(ContentPageMixin, Page):
    """About us page — hero, stats, mission, team, CTA."""

    body = StreamField(PAGE_CONTENT_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("seo_title"), FieldPanel("seo_description")],
            heading=_("SEO"),
        ),
        FieldPanel("body"),
    ]

    subpage_types = []

    class Meta:
        db_table = "content_dynamic_aboutpage"
        verbose_name = _("about page")
        verbose_name_plural = _("about pages")
        app_label = "content"


# ═══════════════════════════════════════════════════════════════════
# FAQ Page
# ═══════════════════════════════════════════════════════════════════

class DynamicFaqPage(ContentPageMixin, Page):
    """FAQ page — hero, faq_groups, CTA."""

    body = StreamField(PAGE_CONTENT_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("seo_title"), FieldPanel("seo_description")],
            heading=_("SEO"),
        ),
        FieldPanel("body"),
    ]

    subpage_types = []

    class Meta:
        db_table = "content_dynamic_faqpage"
        verbose_name = _("FAQ page")
        verbose_name_plural = _("FAQ pages")
        app_label = "content"


# ═══════════════════════════════════════════════════════════════════
# Privacy Page
# ═══════════════════════════════════════════════════════════════════

class DynamicPrivacyPage(ContentPageMixin, Page):
    """Privacy policy page — rich text sections."""

    body = StreamField(PAGE_CONTENT_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("seo_title"), FieldPanel("seo_description")],
            heading=_("SEO"),
        ),
        FieldPanel("body"),
    ]

    subpage_types = []

    class Meta:
        db_table = "content_dynamic_privacypage"
        verbose_name = _("privacy page")
        verbose_name_plural = _("privacy pages")
        app_label = "content"


# ═══════════════════════════════════════════════════════════════════
# Contact Page
# ═══════════════════════════════════════════════════════════════════

class DynamicContactPage(ContentPageMixin, Page):
    """Contact page — hero, contact_methods, form."""

    body = StreamField(PAGE_CONTENT_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("seo_title"), FieldPanel("seo_description")],
            heading=_("SEO"),
        ),
        FieldPanel("body"),
    ]

    subpage_types = []

    class Meta:
        db_table = "content_dynamic_contactpage"
        verbose_name = _("contact page")
        verbose_name_plural = _("contact pages")
        app_label = "content"


# ═══════════════════════════════════════════════════════════════════
# Utility: StreamField → JSON serializer
# ═══════════════════════════════════════════════════════════════════

def _serialize_block_value(value):
    """Convert a StreamField block value to a plain JSON-serializable dict."""
    if isinstance(value, dict):
        return value
    if isinstance(value, RichText):
        return str(value)
    # ListBlock values are lists of StructBlock values
    if isinstance(value, (list, tuple)):
        return list(value)
    try:
        return dict(value)
    except (TypeError, ValueError):
        return str(value)


def page_to_dict(page: Page) -> dict:
    """Convert a Wagtail ContentPageMixin page to the STATIC_PAGES dict format.

    Returns a dict matching the shape of ``STATIC_PAGES[slug]`` so the
    frontend API contract is unchanged.
    """
    seo = getattr(page, "seo_dict", {"title": page.title, "description": ""})
    blocks = []
    if hasattr(page, "body"):
        for block in page.body:
            block_data = _serialize_block_value(block.value)
            if isinstance(block_data, dict):
                block_data["type"] = block.block_type
            blocks.append(block_data)

    return {
        "slug": page.slug,
        "title": page.title,
        "seo": seo,
        "last_updated": getattr(page, "last_updated", None),
        "blocks": blocks,
    }
