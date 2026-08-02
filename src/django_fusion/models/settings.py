"""Reusable settings model bases for Fusion sites."""

import logging

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class AbstractLocalizedSettings(models.Model):
    """Shared language/activation behavior for localized settings records."""

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
            "Designates whether these settings are active for this language. "
            "Only one active per language."
        ),
    )

    class Meta:
        abstract = True

    @classmethod
    def get_active_for_language(cls, language_code):
        return cls.objects.filter(language=language_code, active=True).first()

    @classmethod
    def get_active_for_request(cls, request=None):
        language = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
        active = cls.get_active_for_language(language)
        if active:
            return active

        language_prefix = language.split("-", 1)[0]
        if language_prefix != language:
            active = cls.get_active_for_language(language_prefix)
            if active:
                return active

        return cls.objects.filter(active=True).first()

    @classmethod
    def get_default(cls):
        return cls.objects.filter(active=True).first()

    @classmethod
    def get_all_active(cls):
        return {
            item.language: item
            for item in cls.objects.filter(active=True).order_by("language")
        }

    @classmethod
    def get_available_languages(cls):
        return list(
            cls.objects.filter(active=True)
            .values_list("language", flat=True)
            .distinct()
        )

    def save(self, *args, **kwargs):
        if self.active:
            type(self).objects.filter(
                language=self.language,
                active=True,
            ).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)


class AbstractBrandSettings(AbstractLocalizedSettings):
    """Shared brand and metadata settings behavior."""

    site_name = models.CharField(
        max_length=150,
        default="CTC Hub",
        verbose_name=_("Site Name"),
        help_text=_("Main brand name used across the website."),
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        default="Empowering Digital Transformation",
        verbose_name=_("Tagline"),
        help_text=_("Short descriptive slogan displayed near logo or headers."),
    )
    description = models.TextField(
        blank=True,
        default=(
            "We connect innovation with strategy — empowering brands to grow "
            "through technology."
        ),
        verbose_name=_("Footer Description"),
        help_text=_(
            "Briefly describe the website or company. Often appears in the footer."
        ),
    )
    newsletter_prompt = models.TextField(
        blank=True,
        default=(
            "Join our community of researcher-authors. Get tips, resources, "
            "and updates."
        ),
        verbose_name=_("Newsletter Prompt"),
        help_text=_("Text sitting above the email sign-up form in the footer."),
    )
    marketing_quote = models.CharField(
        max_length=255,
        blank=True,
        default="From Data to Discovery: Write the Future.",
        verbose_name=_("Marketing Quote"),
        help_text=_("A memorable tagline or quote for the footer."),
    )
    title_suffix = models.CharField(
        max_length=255,
        default=" | CTC Hub",
        verbose_name=_("Title suffix"),
        help_text=_("Suffix for <title> tag, e.g. ' | Company Name'"),
    )
    meta_description = models.TextField(
        blank=True,
        default=(
            "CTC Hub delivers innovative web, mobile, and cloud-based digital "
            "solutions for forward-thinking businesses."
        ),
        verbose_name=_("META description"),
    )
    meta_keywords = models.TextField(
        blank=True,
        default="CTC, digital transformation, software, AI, technology, innovation",
        verbose_name=_("META Keywords"),
    )
    meta_author = models.CharField(
        max_length=255,
        blank=True,
        default="CTC Hub Team",
        verbose_name=_("META Author"),
    )

    class Meta:
        abstract = True

    def get_brand_context(self):
        return {
            "name": self.site_name,
            "tagline": self.tagline,
            "description": self.description,
            "newsletter_prompt": self.newsletter_prompt,
            "marketing_quote": self.marketing_quote,
            "language": self.language,
            "is_active": self.active,
        }


class AbstractEmailSettings(AbstractLocalizedSettings):
    """Shared email sender and delivery settings behavior."""

    default_from_email = models.EmailField(
        default="noreply@example.com",
        verbose_name=_("Default From Email"),
    )
    default_from_name = models.CharField(
        max_length=100,
        default="CTC Hub",
        verbose_name=_("Default From Name"),
    )
    enable_tracking = models.BooleanField(
        default=True,
        verbose_name=_("Enable Tracking"),
        help_text=_("Track email opens and clicks in newsletters."),
    )
    use_marketing_consent = models.BooleanField(
        default=True,
        verbose_name=_("Require Marketing Consent"),
        help_text=_("Only send newsletters to users who opted in."),
    )
    max_daily_emails = models.PositiveIntegerField(
        default=1000,
        verbose_name=_("Max Daily Emails"),
        help_text=_("Maximum number of emails that can be sent per day."),
    )
    batch_size = models.PositiveIntegerField(
        default=100,
        verbose_name=_("Batch Size"),
        help_text=_("Emails per sending batch."),
    )
    smtp_server = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("SMTP Server"),
        help_text=_("Optional custom SMTP host for sending."),
    )
    analytics_provider = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Analytics Provider"),
        help_text=_("Optional service for email analytics (e.g., Mailchimp, Sendgrid)."),
    )

    class Meta:
        abstract = True

    def get_sender_identity(self):
        return f"{self.default_from_name} <{self.default_from_email}>"


class AbstractGlobalSettings(models.Model):
    """Shared contact-settings lookup behavior for site models."""

    class Meta:
        abstract = True

    @classmethod
    def get_active_for_request(cls, request=None):
        return cls.objects.first()

    @classmethod
    def get_default(cls):
        return cls.objects.first()

    @classmethod
    def get_all_active(cls):
        return {"all": cls.objects.first()}

    def get_contact_info(self):
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


class AbstractNewsletterSubscription(models.Model):
    """Shared newsletter subscription state behavior."""

    is_subscribed = models.BooleanField(
        default=True,
        verbose_name=_("Is Subscribed"),
        help_text=_("Uncheck to unsubscribe from this newsletter type."),
    )
    last_sent = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Newsletter Sent"),
    )
    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Unsubscribed At"),
        help_text=_("Date and time when user unsubscribed."),
    )

    class Meta:
        abstract = True

    def mark_unsubscribed(self):
        if self.is_subscribed:
            self.is_subscribed = False
            self.unsubscribed_at = timezone.now()
            self.save(update_fields=["is_subscribed", "unsubscribed_at"])
            logger.info(
                "Newsletter subscription unsubscribed: email=%s type=%s.",
                getattr(self, "email", ""),
                getattr(self, "subscription_type", ""),
            )

    def mark_sent(self):
        self.last_sent = timezone.now()
        self.save(update_fields=["last_sent"])
