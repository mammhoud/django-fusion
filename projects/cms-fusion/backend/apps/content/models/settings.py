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
        app_label = "content"
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
        app_label = "content"
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
        app_label = "content"
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
    site_name = models.CharField(max_length=200, default="TharaaEdu",
                                  help_text="Site name displayed in footer/titles")
    site_tagline = models.CharField(max_length=300, blank=True, default="",
                                     help_text="Short tagline")
    logo = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", help_text="Site logo for footer/header",
    )

    # ── Footer content ──
    footer_description = models.TextField(blank=True, default="",
                                           help_text="Company description in footer")
    footer_address = models.CharField(max_length=300, blank=True, default="",
                                       help_text="Physical address")
    footer_phone = models.CharField(max_length=50, blank=True, default="",
                                     help_text="Contact phone number")
    footer_email = models.EmailField(blank=True, default="",
                                      help_text="Contact email")
    footer_copyright = models.CharField(max_length=200, default="© 2025 TharaaEdu. All rights reserved.",
                                         help_text="Copyright text in footer bottom")

    # ── App store links ──
    google_play_url = models.URLField(blank=True, default="", help_text="Google Play store link")
    apple_store_url = models.URLField(blank=True, default="", help_text="Apple App Store link")

    # ── Footer bottom menu ──
    privacy_policy_url = models.CharField(max_length=300, blank=True, default="/contact",
                                           help_text="Link to privacy policy page")
    terms_of_use_url = models.CharField(max_length=300, blank=True, default="/contact",
                                         help_text="Link to terms of use page")

    panels = [
        MultiFieldPanel([
            FieldPanel("site_name"),
            FieldPanel("site_tagline"),
            FieldPanel("logo"),
        ], heading=_("Site Identity")),
        MultiFieldPanel([
            FieldPanel("footer_description"),
            FieldPanel("footer_address"),
            FieldPanel("footer_phone"),
            FieldPanel("footer_email"),
            FieldPanel("footer_copyright"),
        ], heading=_("Footer Content")),
        MultiFieldPanel([
            FieldPanel("google_play_url"),
            FieldPanel("apple_store_url"),
        ], heading=_("App Store Links")),
        MultiFieldPanel([
            FieldPanel("privacy_policy_url"),
            FieldPanel("terms_of_use_url"),
        ], heading=_("Legal Links")),
        InlinePanel("footer_link_groups", label="Footer Link Groups"),
    ]

    class Meta:
        app_label = "content"
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self):
        return f"Site Settings: {self.site_name}"
