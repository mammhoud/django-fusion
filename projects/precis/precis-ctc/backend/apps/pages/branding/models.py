from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class FusionBranding(models.Model):
    """Site-wide branding configuration managed via Wagtail snippets.

    Mirrors the precis-landing FusionBranding pattern so both projects share
    one brand-editing contract (site/company/creator names, colors, favicon,
    logo). Editors update brand identity from the Snippets menu without
    navigating the full SiteSettings panel.
    """

    site_name = models.CharField(max_length=100, default="Fusion",
                                  help_text="Brand name used in the header and meta titles")
    company_name = models.CharField(max_length=100, default="Fusion Inc.",
                                     help_text="Legal company name for footer copyright")
    creator_name = models.CharField(max_length=100, default="Fusion Team",
                                     help_text="Creator/author name for meta tags and credits")
    primary_color = models.CharField(max_length=7, default="#00a1b3",
                                      help_text="Primary brand color (hex)")
    secondary_color = models.CharField(max_length=7, default="#5b21b6",
                                        help_text="Secondary accent color (hex)")
    favicon = models.ImageField(upload_to="branding/", blank=True,
                                 help_text="Upload a favicon image")
    logo = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", help_text="Brand logo (overrides SiteSettings logo when set)",
    )

    panels = [
        MultiFieldPanel([
            FieldPanel("site_name"),
            FieldPanel("company_name"),
            FieldPanel("creator_name"),
        ], heading="Brand Identity"),
        MultiFieldPanel([
            FieldPanel("primary_color"),
            FieldPanel("secondary_color"),
        ], heading="Colors"),
        MultiFieldPanel([
            FieldPanel("favicon"),
            FieldPanel("logo"),
        ], heading="Assets"),
    ]

    class Meta:
        verbose_name = "Fusion Branding"
        verbose_name_plural = "Fusion Branding"

    def __str__(self):
        return self.site_name

    def get_brand_context(self) -> dict:
        """Return brand/theme fields as a frontend-consumable dict."""
        logo_url = None
        if self.logo:
            try:
                logo_url = self.logo.get_rendition("height-60").url
            except Exception:
                pass
        favicon_url = None
        if self.favicon:
            try:
                favicon_url = self.favicon.get_rendition("width-32").url
            except Exception:
                pass
        return {
            "site_name": self.site_name,
            "company_name": self.company_name,
            "creator_name": self.creator_name,
            "logo_url": logo_url,
            "favicon_url": favicon_url,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
        }
