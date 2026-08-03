"""Abstract Certificate (record-keeping) base model for Fusion sites.

Distinct from ``AbstractCertificationTemplate`` which handles certificate
rendering and layout.  This model stores earned/issued certificate records.
"""

import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AbstractCertificate(models.Model):
    """Abstract base for storing certification records."""

    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        VALID = "valid", _("Valid")
        EXPIRED = "expired", _("Expired")
        REVOKED = "revoked", _("Revoked")

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    issuer = models.CharField(max_length=200)
    certificate_id = models.CharField(max_length=100, unique=True, blank=True)
    certificate_url = models.URLField(blank=True)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
    content_object = GenericForeignKey("content_type", "object_id")

    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    verification_status = models.CharField(max_length=50, blank=True)

    certificate_file = models.FileField(upload_to="certificates/", null=True, blank=True)
    verification_file = models.FileField(upload_to="certificates/verification/", null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_verified_set",
    )

    # created_at/updated_at provided by BaseModel

    class Meta:
        abstract = True
        ordering = ["-issue_date"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["issue_date"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.expiry_date and self.issue_date > self.expiry_date:
            raise ValidationError(_("Issue date must be before expiry date."))

    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        delta = self.expiry_date - timezone.now().date()
        return delta.days

    def verify(self, verified_by_user, verification_status="verified"):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.verified_by = verified_by_user
        self.verification_status = verification_status
        self.status = self.StatusChoices.VALID
        self.save()

    def revoke(self, reason=""):
        self.status = self.StatusChoices.REVOKED
        self.verification_status = f"revoked: {reason}"
        self.save()
