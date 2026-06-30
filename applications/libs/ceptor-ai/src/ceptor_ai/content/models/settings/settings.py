from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
)
from wagtail.fields import StreamField
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
)
from wagtail.search import index

from ceptor_ai.content.blocks.contact.social_links import SocialLinkBlock

LANGUAGE_CODE = settings.LANGUAGE_CODE


# =======================================
# WEBSITE SETTINGS
# =======================================
class TechBridges(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    ClusterableModel,
    index.Indexed,
):
    """
    Global website branding, metadata, and visual identity settings.
    """

    # --- Brand Identity ---
    site_name = models.CharField(
        _("Site Name"),
        max_length=150,
        default="CTC Hub",
        help_text=_("Main brand name used across the website."),
    )
    tagline = models.CharField(
        _("Tagline"),
        max_length=255,
        blank=True,
        default="Empowering Digital Transformation",
        help_text=_("Short descriptive slogan displayed near logo or headers."),
    )

    # --- Language & Status ---
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default="en",
        verbose_name=_("Language Code"),
        help_text=_("Language code for these settings (e.g., 'en', 'fr')."),
    )
    active = models.BooleanField(
        default=False,
        verbose_name=_("Active"),
        help_text=_(
            "Designates whether these settings are active for this language. Only one active per language."
        ),
    )

    # --- SEO / META & Footer Text ---
    description = models.TextField(
        blank=True,
        verbose_name=_("Footer Description"),
        default="We connect innovation with strategy — empowering brands to grow through technology.",
        help_text=_("Briefly describe the website or company. Often appears in the footer."),
    )
    newsletter_prompt = models.TextField(
        blank=True,
        verbose_name=_("Newsletter Prompt"),
        default="Join our community of researcher-authors. Get tips, resources, and updates.",
        help_text=_("Text sitting above the email sign-up form in the footer."),
    )
    marketing_quote = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Marketing Quote"),
        default="From Data to Discovery: Write the Future.",
        help_text=_("A memorable tagline or quote for the footer."),
    )
    title_suffix = models.CharField(
        verbose_name=_("Title suffix"),
        max_length=255,
        help_text=_("Suffix for <title> tag, e.g. ' | Company Name'"),
        default=" | CTC Hub",
    )
    meta_description = models.TextField(
        _("META description"),
        blank=True,
        default="CTC Hub delivers innovative web, mobile, and cloud-based digital solutions for forward-thinking businesses.",
    )
    meta_keywords = models.TextField(
        _("META Keywords"),
        blank=True,
        default="CTC, digital transformation, software, AI, technology, innovation",
    )
    meta_author = models.CharField(
        _("META Author"),
        max_length=255,
        blank=True,
        default="CTC Hub Team",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("language"),
                        FieldPanel("active"),
                    ]
                ),
            ],
            heading=_("Language Configuration"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("site_name"),
                FieldPanel("tagline"),
            ],
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
        """Validate that only one active setting exists per language."""
        from django.core.exceptions import ValidationError

        super().clean()

        if self.active:
            # Check if another active setting exists for the same language
            existing_active = TechBridges.objects.filter(
                language=self.language, active=True
            ).exclude(pk=self.pk)

            if existing_active.exists():
                raise ValidationError(
                    {
                        "active": f"Another active TechBridges already exists for language {self.get_language_display()}."
                    }
                )

    def save(self, *args, **kwargs):
        # Ensure only one active setting per language
        if self.active:
            # Deactivate all other settings for this language
            TechBridges.objects.filter(language=self.language, active=True).exclude(
                pk=self.pk
            ).update(active=False)

        super().save(*args, **kwargs)

    def get_brand_context(self):
        """Return key brand details for templates."""
        return {
            "name": self.site_name,
            "tagline": self.tagline,
            "description": self.description,
            "newsletter_prompt": self.newsletter_prompt,
            "marketing_quote": self.marketing_quote,
            "language": self.language,
            "is_active": self.active,
        }


    @classmethod
    def get_active_for_language(cls, language_code):
        """
        Get active site settings for a specific language.

        Args:
            language_code: Language code (e.g., 'en', 'fr')

        Returns:
            TechBridges instance or None
        """
        try:
            return cls.objects.get(language=language_code, active=True)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_active_for_request(cls, request=None):
        """
        Get active site settings for the current request with language fallback.

        Priority:
        1. Active settings for exact language code
        2. Active settings for language prefix (e.g., 'en' for 'en-us')
        3. First active settings found (as fallback)
        """
        # Get language from request
        language = getattr(request, "LANGUAGE_CODE", LANGUAGE_CODE)

        # Try exact language match
        settings = cls.get_active_for_language(language)
        if settings:
            return settings

        # Try language prefix if different from full language code
        if "-" in language:
            language_prefix = language.split("-")[0]
            settings = cls.get_active_for_language(language_prefix)
            if settings:
                return settings

        # Fallback to any active settings (first one)
        try:
            return cls.objects.filter(active=True).first()
        except cls.DoesNotExist:
            return cls.activate_language(language_prefix)

    @classmethod
    def get_default(cls):
        """Get the first active settings as default."""
        try:
            return cls.objects.filter(active=True).first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_all_active(cls):
        """Get all active settings, organized by language."""
        return {
            settings.language: settings
            for settings in cls.objects.filter(active=True).order_by("language")
        }

    @classmethod
    def get_available_languages(cls):
        """Get list of languages with active settings."""
        return list(cls.objects.filter(active=True).values_list("language", flat=True).distinct())

    @classmethod
    def activate_language(cls, language_code):
        """
        Activate settings for a specific language.
        If settings don't exist for that language, create default ones.
        """
        try:
            # Try to get existing settings for this language
            settings = cls.objects.get(language=language_code)
            settings.active = True
            settings.save()
            return settings
        except cls.DoesNotExist:
            # Create default settings for this language
            default_settings = cls.get_default()
            if default_settings:
                # Clone default settings for new language
                settings = cls.objects.create(
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
                return settings
        return None


# =======================================
# GLOBAL CONTACT & BRAND SETTINGS
# =======================================
class GlobalSettings(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    ClusterableModel,
    index.Indexed,
):
    """Site-wide contact details, social profiles, and communication channels."""

    # --- Contact Info ---
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
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email"),
        default="info@example.com",
    )
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

    # --- Social Media ---
    social_links = StreamField(
        [("link", SocialLinkBlock())],
        use_json_field=True,
        verbose_name=_("Social links"),
        blank=True,
        help_text=_("Add links to your social media profiles"),
    )



    panels = [
        MultiFieldPanel(
            [
                FieldPanel("logo"),
                FieldPanel("favicon"),
            ],
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
        return f"Global Brand & Contact Settings"

    def clean(self):
        super().clean()

    @classmethod
    def get_active_for_request(cls, request=None):
        return cls.objects.first()

    @classmethod
    def get_default(cls):
        return cls.objects.first()

    @classmethod
    def get_all_active(cls):
        return {"all": cls.objects.first()}

    # --- Helpers ---
    def get_social_links(self):
        """Return structured list of valid social links."""
        return [block.value for block in self.social_links if block.value.get("url")]

    def get_contact_info(self):
        """Return contact details for rendering."""
        return {
            "phone": self.phone_number,
            "whatsapp": self.whatsapp_number,
            "email": self.email,
            "support": self.support_email,
            "address": self.address,
            "maps_link": self.google_maps_link,
            "organisation": self.organisation_url,
            "additional_info": self.additional_info,
        }
