"""
Privacy Consent Model

Tracks user consent to privacy policies and terms of service.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class PrivacyPolicy(models.Model):
    """Represents a privacy policy version."""

    title = models.CharField(max_length=255, default="Privacy Policy")
    version = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-created_at"]
        verbose_name = "Privacy Policy"
        verbose_name_plural = "Privacy Policies"

    def __str__(self):
        return f"{self.title} v{self.version}"


class PrivacyConsent(models.Model):
    """Tracks user consent to privacy policies."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="%(app_label)s_privacy_consent"
    )
    policy = models.ForeignKey(
        PrivacyPolicy, on_delete=models.PROTECT, related_name="consents"
    )
    consented_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-consented_at"]
        verbose_name = "Privacy Consent"
        verbose_name_plural = "Privacy Consents"
        unique_together = ("user", "policy")

    def __str__(self):
        return f"{self.user.email} - {self.policy.version}"

    @classmethod
    def has_consented(cls, user, policy=None):
        """Check if user has consented to the privacy policy."""
        if policy is None:
            policy = PrivacyPolicy.objects.filter(is_active=True).first()

        if not policy:
            return False

        return cls.objects.filter(
            user=user, policy=policy, is_active=True
        ).exists()

    @classmethod
    def record_consent(cls, user, policy=None, ip_address=None, user_agent=None):
        """Record user consent to privacy policy."""
        if policy is None:
            policy = PrivacyPolicy.objects.filter(is_active=True).first()

        if not policy:
            raise ValueError("No active privacy policy found")

        consent, created = cls.objects.update_or_create(
            user=user,
            policy=policy,
            defaults={
                "ip_address": ip_address,
                "user_agent": user_agent,
                "is_active": True,
                "consented_at": timezone.now(),
            },
        )

        return consent, created


class TermsOfService(models.Model):
    """Represents a terms of service version."""

    title = models.CharField(max_length=255, default="Terms of Service")
    version = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-created_at"]
        verbose_name = "Terms of Service"
        verbose_name_plural = "Terms of Service"

    def __str__(self):
        return f"{self.title} v{self.version}"


class TermsConsent(models.Model):
    """Tracks user consent to terms of service."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="%(app_label)s_terms_consent"
    )
    terms = models.ForeignKey(
        TermsOfService, on_delete=models.PROTECT, related_name="consents"
    )
    consented_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-consented_at"]
        verbose_name = "Terms Consent"
        verbose_name_plural = "Terms Consents"
        unique_together = ("user", "terms")

    def __str__(self):
        return f"{self.user.email} - {self.terms.version}"

    @classmethod
    def has_consented(cls, user, terms=None):
        """Check if user has consented to the terms of service."""
        if terms is None:
            terms = TermsOfService.objects.filter(is_active=True).first()

        if not terms:
            return False

        return cls.objects.filter(
            user=user, terms=terms, is_active=True
        ).exists()

    @classmethod
    def record_consent(cls, user, terms=None, ip_address=None, user_agent=None):
        """Record user consent to terms of service."""
        if terms is None:
            terms = TermsOfService.objects.filter(is_active=True).first()

        if not terms:
            raise ValueError("No active terms of service found")

        consent, created = cls.objects.update_or_create(
            user=user,
            terms=terms,
            defaults={
                "ip_address": ip_address,
                "user_agent": user_agent,
                "is_active": True,
                "consented_at": timezone.now(),
            },
        )

        return consent, created
