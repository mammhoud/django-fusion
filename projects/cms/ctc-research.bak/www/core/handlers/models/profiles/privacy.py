"""
Privacy Consent Models

Tracks user consent to privacy policies and terms of service.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class PrivacyPolicy(models.Model):
    """Represents a versioned privacy policy."""

    title = models.CharField(_("title"), max_length=255, default=_("Privacy Policy"))
    version = models.CharField(_("version"), max_length=50, unique=True)
    content = models.TextField(_("content"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Privacy Policy")
        verbose_name_plural = _("Privacy Policies")

    def __str__(self) -> str:
        return f"{self.title} v{self.version}"


class PrivacyConsent(models.Model):
    """Tracks user consent to a specific privacy policy version."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_privacy_consent",
        verbose_name=_("user"),
    )
    policy = models.ForeignKey(
        PrivacyPolicy,
        on_delete=models.PROTECT,
        related_name="consents",
        verbose_name=_("policy"),
    )
    consented_at = models.DateTimeField(_("consented at"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["-consented_at"]
        verbose_name = _("Privacy Consent")
        verbose_name_plural = _("Privacy Consents")
        unique_together = ("user", "policy")

    def __str__(self) -> str:
        return f"{self.user.email} — {self.policy.version}"

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    @classmethod
    def has_consented(cls, user, policy=None) -> bool:
        """Return True if *user* has an active consent for *policy*."""
        if not user or not user.is_authenticated:
            return False
        if policy is None:
            policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if not policy:
            return False
        return cls.objects.filter(user=user, policy=policy, is_active=True).exists()

    @classmethod
    def record_consent(cls, user, policy=None, ip_address=None, user_agent=None):
        """
        Create or update a consent record for *user*.

        Returns:
            (PrivacyConsent, created: bool)
        """
        if policy is None:
            policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if not policy:
            raise ValueError(_("No active privacy policy found."))

        return cls.objects.update_or_create(
            user=user,
            policy=policy,
            defaults={
                "ip_address": ip_address,
                "user_agent": user_agent or "",
                "is_active": True,
                "consented_at": timezone.now(),
            },
        )


class TermsOfService(models.Model):
    """Represents a versioned terms of service document."""

    title = models.CharField(_("title"), max_length=255, default=_("Terms of Service"))
    version = models.CharField(_("version"), max_length=50, unique=True)
    content = models.TextField(_("content"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Terms of Service")
        verbose_name_plural = _("Terms of Service")

    def __str__(self) -> str:
        return f"{self.title} v{self.version}"


class TermsConsent(models.Model):
    """Tracks user consent to a specific terms of service version."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_terms_consent",
        verbose_name=_("user"),
    )
    terms = models.ForeignKey(
        TermsOfService,
        on_delete=models.PROTECT,
        related_name="consents",
        verbose_name=_("terms"),
    )
    consented_at = models.DateTimeField(_("consented at"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["-consented_at"]
        verbose_name = _("Terms Consent")
        verbose_name_plural = _("Terms Consents")
        unique_together = ("user", "terms")

    def __str__(self) -> str:
        return f"{self.user.email} — {self.terms.version}"

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    @classmethod
    def has_consented(cls, user, terms=None) -> bool:
        """Return True if *user* has an active consent for *terms*."""
        if not user or not user.is_authenticated:
            return False
        if terms is None:
            terms = TermsOfService.objects.filter(is_active=True).first()
        if not terms:
            return False
        return cls.objects.filter(user=user, terms=terms, is_active=True).exists()

    @classmethod
    def record_consent(cls, user, terms=None, ip_address=None, user_agent=None):
        """
        Create or update a consent record for *user*.

        Returns:
            (TermsConsent, created: bool)
        """
        if terms is None:
            terms = TermsOfService.objects.filter(is_active=True).first()
        if not terms:
            raise ValueError(_("No active terms of service found."))

        return cls.objects.update_or_create(
            user=user,
            terms=terms,
            defaults={
                "ip_address": ip_address,
                "user_agent": user_agent or "",
                "is_active": True,
                "consented_at": timezone.now(),
            },
        )
