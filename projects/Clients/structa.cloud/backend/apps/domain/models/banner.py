"""
AnnouncementBanner — Top-of-page panel snippet.

Provides admin-modifiable banner at the top of all pages with:
- Marquee scrolling text
- Social links with icons
- Discount/promotion percentage display
- Customizable colors (background, text, accent)
- Active/inactive toggle

Part of TechBridgesSnippetGroup.
"""
from colorfield.fields import ColorField
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import DraftStateMixin, RevisionMixin

from apps.domain.blocks.contact.social_links import SocialLinkBlock


class AnnouncementBanner(
    DraftStateMixin,
    RevisionMixin,
    ClusterableModel,
):
    """
    Top-of-page announcement banner with marquee, social links, and promotions.
    Managed via Wagtail admin. Part of Brand Settings group.
    """

    # === Identity ===
    name = models.CharField(
        max_length=255,
        verbose_name=_("Banner Name"),
        help_text=_("Internal name for this banner configuration."),
        default="Default Banner",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Only active banners are displayed on the site."),
    )

    # === Marquee Text ===
    marquee_text = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Marquee Text"),
        help_text=_("Scrolling announcement text. Leave blank to hide marquee."),
        default="🎓 New courses available! Enroll now and start learning today.",
    )
    marquee_speed = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Marquee Speed (seconds)"),
        help_text=_("Duration of one full scroll cycle in seconds. Higher = slower."),
    )

    # === Discount / Promotion ===
    show_discount = models.BooleanField(
        default=False,
        verbose_name=_("Show Discount Badge"),
    )
    discount_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Discount %"),
        help_text=_("Percentage value for the discount badge (e.g. 20 for 20%)."),
    )
    discount_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Discount Text"),
        help_text=_("Text next to the discount badge (e.g. 'OFF on all courses')."),
        default="OFF on all courses",
    )
    discount_link = models.URLField(
        blank=True,
        verbose_name=_("Discount Link"),
        help_text=_("URL the discount badge links to."),
    )

    # === Colors ===
    background_color = ColorField(
        default="#1a1a2e",
        verbose_name=_("Background Color"),
    )
    text_color = ColorField(
        default="#ffffff",
        verbose_name=_("Text Color"),
    )
    accent_color = ColorField(
        default="#e94560",
        verbose_name=_("Accent Color"),
        help_text=_("Used for discount badge, links, and highlights."),
    )
    marquee_background = ColorField(
        default="#16213e",
        verbose_name=_("Marquee Background"),
    )

    # === Social Links ===
    show_social_links = models.BooleanField(
        default=True,
        verbose_name=_("Show Social Links"),
    )
    social_links = StreamField(
        [("link", SocialLinkBlock())],
        use_json_field=True,
        verbose_name=_("Social Links"),
        blank=True,
        help_text=_("Social media icons displayed in the banner."),
    )

    # === Quick Links ===
    quick_links_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Quick Links Text"),
        help_text=_("Optional text label before quick links (e.g. 'Contact:')."),
    )
    phone_display = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Phone Number"),
        help_text=_("Phone number displayed in the banner."),
    )
    email_display = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Email"),
        help_text=_("Email displayed in the banner."),
    )

    # === Panels ===
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("is_active"),
            ],
            heading=_("Identity"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("marquee_text"),
                FieldPanel("marquee_speed"),
            ],
            heading=_("Marquee"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_discount"),
                FieldRowPanel([
                    FieldPanel("discount_percentage"),
                    FieldPanel("discount_text"),
                ]),
                FieldPanel("discount_link"),
            ],
            heading=_("Discount / Promotion"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("background_color"),
                    FieldPanel("text_color"),
                ]),
                FieldRowPanel([
                    FieldPanel("accent_color"),
                    FieldPanel("marquee_background"),
                ]),
            ],
            heading=_("Colors"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_social_links"),
                FieldPanel("social_links"),
            ],
            heading=_("Social Links"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("quick_links_text"),
                FieldRowPanel([
                    FieldPanel("phone_display"),
                    FieldPanel("email_display"),
                ]),
            ],
            heading=_("Quick Contact"),
        ),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared"
        verbose_name = _("Announcement Banner")
        verbose_name_plural = _("Announcement Banners")
        ordering = ["-is_active", "-updated_at"]

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name}"

    @classmethod
    def get_active(cls):
        """Return the first active banner, or None."""
        return cls.objects.filter(is_active=True).first()

    def get_social_links_list(self):
        """Return structured list of social links."""
        return [block.value for block in self.social_links if block.value.get("url")]
