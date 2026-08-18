"""
Wagtail-managed site settings — Social links, footer content, site identity.

These replace the hardcoded static data in next-LMS:
  - components/common/Social.tsx (5 hardcoded social links)
  - layouts/footers/FooterCommon.tsx (hardcoded address, phone, links)
  - layouts/footers/FooterOne.tsx (copyright text)

Served via: GET /apis/site/settings
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.snippets.models import register_snippet

# ═══════════════════════════════════════════════════════════════════
# Social Links (Wagtail snippet)
# ═══════════════════════════════════════════════════════════════════

PLATFORM_CHOICES = [
    ("facebook", "Facebook"),
    ("twitter", "Twitter / X"),
    ("instagram", "Instagram"),
    ("linkedin", "LinkedIn"),
    ("youtube", "YouTube"),
    ("whatsapp", "WhatsApp"),
    ("tiktok", "TikTok"),
    ("github", "GitHub"),
    ("discord", "Discord"),
    ("other", "Other"),
]


@register_snippet
class SocialLink(models.Model):
    """A social media link displayed in the footer and header."""

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="facebook")
    label = models.CharField(max_length=100, blank=True, default="",
                              help_text="Display name (e.g., 'Follow us on Facebook')")
    url = models.URLField(max_length=300)
    icon_svg = models.CharField(max_length=200, blank=True, default="",
                                 help_text="Path to SVG icon (e.g., '/assets/img/icons/facebook.svg')")
    icon_class = models.CharField(max_length=100, blank=True, default="",
                                   help_text="CSS class for icon font (e.g., 'fab fa-facebook')")
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.IntegerField(default=0)

    panels = [
        FieldPanel("platform"),
        FieldPanel("label"),
        FieldPanel("url"),
        MultiFieldPanel([
            FieldPanel("icon_svg"),
            FieldPanel("icon_class"),
        ], heading=_("Icon")),
        MultiFieldPanel([
            FieldPanel("is_active"),
            FieldPanel("sort_order"),
        ], heading=_("Display")),
    ]

    class Meta:
        # ContentConfig uses the historical ``pages`` label; keep these
        # settings/snippet models on that migration graph as well.
        app_label = "pages"
        verbose_name = _("social link")
        verbose_name_plural = _("social links")
        ordering = ["sort_order", "platform"]

    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"


# ═══════════════════════════════════════════════════════════════════
# Footer Link Groups (inline model for SiteSettings)
# ═══════════════════════════════════════════════════════════════════

class FooterLinkGroup(ClusterableModel):
    """A group of links in the footer (e.g., 'Useful Links', 'Our Company')."""

    setting = ParentalKey(
        "SiteSettings", on_delete=models.CASCADE, related_name="footer_link_groups",
    )
    title = models.CharField(max_length=100, help_text="e.g., 'Useful Links', 'Our Company'")
    sort_order = models.IntegerField(default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("sort_order"),
        InlinePanel("links", label="Links"),
    ]

    class Meta:
        # ContentConfig uses the historical ``pages`` label; keep these
        # settings/snippet models on that migration graph as well.
        app_label = "pages"
        ordering = ["sort_order"]


class FooterLink(models.Model):
    """A single link within a footer link group."""

    group = ParentalKey(
        FooterLinkGroup, on_delete=models.CASCADE, related_name="links",
    )
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=300)
    sort_order = models.IntegerField(default=0)

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        # ContentConfig uses the historical ``pages`` label; keep these
        # settings/snippet models on that migration graph as well.
        app_label = "pages"
        ordering = ["sort_order"]


# ═══════════════════════════════════════════════════════════════════
# Site Settings (Wagtail BaseSiteSetting)
# ═══════════════════════════════════════════════════════════════════

@register_setting
class SiteSettings(BaseSiteSetting, ClusterableModel):
    """Global site settings managed via Wagtail admin.

    Served via: GET /apis/site/settings
    Replaces hardcoded content in FooterCommon.tsx, FooterOne.tsx, Social.tsx.
    """

    # ── Site identity ──
    site_name = models.CharField(max_length=200, default="CTC Research",
                                  help_text="Site name displayed in footer/titles")
    site_tagline = models.CharField(max_length=300, blank=True, default="",
                                     help_text="Short tagline")
    logo = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", help_text="Site logo for footer/header",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", help_text="Favicon (auto-sized to 32x32)",
    )

    # ── SEO & metadata ──
    meta_description = models.TextField(blank=True, default="",
        help_text="Default meta description for pages without one")
    meta_keywords = models.CharField(max_length=300, blank=True, default="",
        help_text="Comma-separated keywords")
    meta_author = models.CharField(max_length=200, blank=True, default="",
        help_text="Default meta author")
    og_image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", help_text="Default Open Graph image (1200x630 recommended)",
    )
    twitter_handle = models.CharField(max_length=50, blank=True, default="",
        help_text="Twitter/X handle (without @)")

    # ── Analytics ──
    google_tag_manager_id = models.CharField(max_length=30, blank=True, default="",
        help_text="GTM container ID (e.g., GTM-XXXXXXX)")
    google_analytics_id = models.CharField(max_length=30, blank=True, default="",
        help_text="GA4 measurement ID (e.g., G-XXXXXXXX)")
    analytics_provider = models.CharField(max_length=50, blank=True, default="",
        choices=[("", "None"), ("gtm", "Google Tag Manager"), ("ga4", "Google Analytics 4"),
                 ("plausible", "Plausible"), ("umami", "Umami")],
        help_text="Analytics provider for the frontend")

    # ── Navigation ──
    nav_show_home = models.BooleanField(default=True,
        help_text="Include Home in the main navigation")
    nav_show_contact = models.BooleanField(default=True,
        help_text="Show contact link in header CTA area")
    nav_cta_label = models.CharField(max_length=50, blank=True, default="",
        help_text="CTA button label in header")
    nav_cta_url = models.CharField(max_length=300, blank=True, default="/contact",
        help_text="CTA button link in header")

    # ── Brand / theme ──
    primary_color = models.CharField(max_length=7, blank=True, default="#00a1b3",
        help_text="Primary brand color (hex)")
    accent_color = models.CharField(max_length=7, blank=True, default="#008080",
        help_text="Accent color for highlights (hex)")

    # ── Footer content ──
    footer_description = models.TextField(blank=True, default="",
                                           help_text="Company description in footer")
    footer_address = models.CharField(max_length=300, blank=True, default="",
                                       help_text="Physical address")
    footer_phone = models.CharField(max_length=50, blank=True, default="",
                                     help_text="Contact phone number")
    footer_email = models.EmailField(blank=True, default="",
                                      help_text="Contact email")
    footer_copyright = models.CharField(max_length=200, default="© 2026 CTC Research. All rights reserved.",
                                         help_text="Copyright text in footer bottom")
    footer_banner_enabled = models.BooleanField(default=False,
        help_text="Show a site-wide announcement banner above the footer")
    footer_banner_text = models.TextField(blank=True, default="",
        help_text="Announcement text. HTML allowed. Shown when enabled above.")
    footer_banner_style = models.CharField(max_length=20, blank=True, default="",
        choices=[("", "None"), ("info", "Info (blue)"), ("offer", "Offer (amber)"),
                 ("alert", "Alert (red)"), ("success", "Success (green)")],
        help_text="Visual style for the announcement banner")
    footer_text_secondary = models.TextField(blank=True, default="",
        help_text="Secondary footer text row (e.g., 'Proudly built in MENA region')")
    newsletter_prompt = models.TextField(blank=True, default="",
        help_text="Text above the newsletter signup in footer")

    # ── App store links ──
    google_play_url = models.URLField(blank=True, default="", help_text="Google Play store link")
    apple_store_url = models.URLField(blank=True, default="", help_text="Apple App Store link")

    # ── Footer bottom menu ──
    privacy_policy_url = models.CharField(max_length=300, blank=True, default="/contact",
                                           help_text="Link to privacy policy page")
    terms_of_use_url = models.CharField(max_length=300, blank=True, default="/contact",
                                         help_text="Link to terms of use page")

    # ── Chat / contact widget ──
    chat_enabled = models.BooleanField(default=False,
        help_text="Enable live chat / contact widget")
    chat_provider = models.CharField(max_length=50, blank=True, default="",
        choices=[("", "None"), ("crisp", "Crisp"), ("intercom", "Intercom"),
                 ("tawk", "Tawk.to")],
        help_text="Chat widget provider")
    chat_widget_id = models.CharField(max_length=100, blank=True, default="",
        help_text="Chat widget ID / website ID")

    panels = [
        MultiFieldPanel([
            FieldPanel("site_name"),
            FieldPanel("site_tagline"),
            FieldPanel("logo"),
            FieldPanel("favicon"),
        ], heading=_("Site Identity")),
        MultiFieldPanel([
            FieldPanel("meta_description"),
            FieldPanel("meta_keywords"),
            FieldPanel("meta_author"),
            FieldPanel("og_image"),
            FieldPanel("twitter_handle"),
        ], heading=_("SEO & Metadata")),
        MultiFieldPanel([
            FieldPanel("analytics_provider"),
            FieldPanel("google_tag_manager_id"),
            FieldPanel("google_analytics_id"),
        ], heading=_("Analytics")),
        MultiFieldPanel([
            FieldPanel("nav_show_home"),
            FieldPanel("nav_show_contact"),
            FieldPanel("nav_cta_label"),
            FieldPanel("nav_cta_url"),
        ], heading=_("Navigation")),
        MultiFieldPanel([
            FieldPanel("primary_color"),
            FieldPanel("accent_color"),
        ], heading=_("Brand Colors")),
        MultiFieldPanel([
            FieldPanel("footer_banner_enabled"),
            FieldPanel("footer_banner_text"),
            FieldPanel("footer_banner_style"),
        ], heading=_("Announcement Banner")),
        MultiFieldPanel([
            FieldPanel("footer_description"),
            FieldPanel("footer_address"),
            FieldPanel("footer_phone"),
            FieldPanel("footer_email"),
            FieldPanel("footer_copyright"),
            FieldPanel("footer_text_secondary"),
            FieldPanel("newsletter_prompt"),
        ], heading=_("Footer Content")),
        MultiFieldPanel([
            FieldPanel("google_play_url"),
            FieldPanel("apple_store_url"),
        ], heading=_("App Store Links")),
        MultiFieldPanel([
            FieldPanel("privacy_policy_url"),
            FieldPanel("terms_of_use_url"),
        ], heading=_("Legal Links")),
        MultiFieldPanel([
            FieldPanel("chat_enabled"),
            FieldPanel("chat_provider"),
            FieldPanel("chat_widget_id"),
        ], heading=_("Chat Widget")),
        InlinePanel("footer_link_groups", label="Footer Link Groups"),
    ]

    class Meta:
        # ContentConfig uses the historical ``pages`` label; keep these
        # settings/snippet models on that migration graph as well.
        app_label = "pages"
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self):
        return f"Site Settings: {self.site_name}"

    def get_seo_context(self) -> dict:
        """Return SEO fields as a frontend-consumable dict."""
        return {
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "meta_author": self.meta_author,
            "og_image_url": self.og_image.get_rendition("width-1200").url if self.og_image else None,
            "twitter_handle": self.twitter_handle,
        }

    def get_analytics_context(self) -> dict:
        """Return analytics fields as a frontend-consumable dict."""
        return {
            "provider": self.analytics_provider,
            "gtm_id": self.google_tag_manager_id,
            "ga4_id": self.google_analytics_id,
        }
