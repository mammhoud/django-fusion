from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import DraftStateMixin, PreviewableMixin, RevisionMixin
from wagtail.search import index

from django_fusion.models.settings import AbstractBrandSettings, AbstractGlobalSettings

from apps.domain.blocks.contact.social_links import SocialLinkBlock


class TechBridges(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    ClusterableModel,
    AbstractBrandSettings,
    index.Indexed,
):
    """Global website branding, metadata, and visual identity settings."""

    panels = [
        MultiFieldPanel(
            [FieldRowPanel([FieldPanel("language"), FieldPanel("active")])],
            heading=_("Language Configuration"),
        ),
        MultiFieldPanel(
            [FieldPanel("site_name"), FieldPanel("tagline")],
            heading=_("Brand Identity"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("description"),
                FieldPanel("newsletter_prompt"),
                FieldPanel("marketing_quote"),
            ],
            heading=_("Footer Content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("title_suffix"),
                FieldPanel("meta_description"),
                FieldPanel("meta_keywords"),
                FieldPanel("meta_author"),
            ],
            heading=_("SEO & Meta Information"),
        ),
    ]

    class Meta:
        app_label = "shared"
        verbose_name = _("Tech Bridges")
        verbose_name_plural = _("Tech Bridges")
        constraints = [
            models.UniqueConstraint(
                fields=["language"],
                condition=models.Q(active=True),
                name="unique_active_brand_settings_per_language",
            ),
        ]

    def __str__(self):
        status = "✓" if self.active else "✗"
        return f"{self.site_name} Settings ({self.get_language_display()}) {status}"

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        if self.active and type(self).objects.filter(
            language=self.language,
            active=True,
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                {
                    "active": (
                        "Another active TechBridges already exists for language "
                        f"{self.get_language_display()}."
                    )
                }
            )

    @classmethod
    def activate_language(cls, language_code):
        settings = cls.objects.filter(language=language_code).first()
        if settings:
            settings.active = True
            settings.save()
            return settings

        default_settings = cls.get_default()
        if not default_settings:
            return None

        return cls.objects.create(
            language=language_code,
            active=True,
            site_name=default_settings.site_name,
            tagline=default_settings.tagline,
            description=default_settings.description,
            newsletter_prompt=default_settings.newsletter_prompt,
            marketing_quote=default_settings.marketing_quote,
            title_suffix=default_settings.title_suffix,
            meta_description=default_settings.meta_description,
            meta_keywords=default_settings.meta_keywords,
            meta_author=default_settings.meta_author,
        )


class GlobalSettings(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    ClusterableModel,
    AbstractGlobalSettings,
    index.Indexed,
):
    """Site-wide contact details, social profiles, and communication channels."""

    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Favicon"),
        help_text=_("Small icon used in browser tabs and bookmarks."),
    )
    phone_number = models.CharField(
        max_length=24,
        blank=True,
        verbose_name=_("Phone number"),
        default="+1 800 123 4567",
    )
    whatsapp_number = models.CharField(
        max_length=24,
        blank=True,
        verbose_name=_("WhatsApp number"),
        help_text=_("Optional WhatsApp business contact."),
        default="+1 800 765 4321",
    )
    email = models.EmailField(blank=True, verbose_name=_("Email"), default="info@example.com")
    support_email = models.EmailField(
        blank=True,
        verbose_name=_("Support Email"),
        default="support@example.com",
    )
    address = models.TextField(
        blank=True,
        verbose_name=_("Address"),
        default="123 Innovation Drive, San Francisco, CA 94105",
    )
    google_maps_link = models.URLField(
        blank=True,
        verbose_name=_("Google Maps Link"),
        help_text=_("Optional map link for location directions."),
    )
    organisation_url = models.URLField(
        verbose_name=_("Organisation URL"),
        blank=True,
        default="https://www.ctchub.com",
    )
    additional_info = models.TextField(
        verbose_name=_("Additional Information"),
        blank=True,
        default="Open Monday – Friday, 9:00am – 6:00pm (PST).",
    )
    social_links = StreamField(
        [("link", SocialLinkBlock())],
        use_json_field=True,
        verbose_name=_("Social links"),
        blank=True,
        help_text=_("Add links to your social media profiles"),
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel("logo"), FieldPanel("favicon")],
            heading=_("Branding Settings (Non-translated)"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel("phone_number"), FieldPanel("whatsapp_number")]),
                FieldRowPanel([FieldPanel("email"), FieldPanel("support_email")]),
                FieldPanel("address"),
                FieldPanel("google_maps_link"),
                FieldPanel("organisation_url"),
                FieldPanel("additional_info"),
            ],
            heading=_("Contact & Organisation Info"),
        ),
        FieldPanel("social_links"),
    ]

    class Meta:
        verbose_name = _("Global Settings")
        verbose_name_plural = _("Global Settings")

    def __str__(self):
        return "Global Brand & Contact Settings"

    def clean(self):
        super().clean()

    def get_social_links(self):
        return [block.value for block in self.social_links if block.value.get("url")]
