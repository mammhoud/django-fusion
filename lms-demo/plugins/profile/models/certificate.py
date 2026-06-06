import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_osoul.models import BaseModel as DefaultBase
from django_rseal.workflows.pipelines.models.tags import *

User = get_user_model()

class Certificate(DefaultBase):
    """
    Certificate model for storing certifications.
    """
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('Pending')
        VALID = 'valid', _('Valid')
        EXPIRED = 'expired', _('Expired')
        REVOKED = 'revoked', _('Revoked')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    issuer = models.CharField(max_length=200)
    certificate_id = models.CharField(max_length=100, unique=True, blank=True)
    certificate_url = models.URLField(blank=True)

    # Generic foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Dates
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    verification_status = models.CharField(max_length=50, blank=True)

    # Files
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    verification_file = models.FileField(upload_to='certificates/verification/', null=True, blank=True)

    # Metadata
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # tags = models.ManyToManyField(Tag, blank=True, related_name='certificates')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['status']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['expiry_date']),
        ]
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')

    def __str__(self):
        return self.name

    def clean(self):
        if self.expiry_date and self.issue_date > self.expiry_date:
            raise ValidationError(_('Issue date must be before expiry date.'))

    @property
    def is_expired(self):
        """Check if certificate is expired."""
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def days_until_expiry(self):
        """Calculate days until expiry."""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - timezone.now().date()
        return delta.days

    def verify(self, verified_by_user, verification_status='verified'):
        """Mark certificate as verified."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.verified_by = verified_by_user
        self.verification_status = verification_status
        self.status = self.StatusChoices.VALID
        self.save()

    def revoke(self, reason=''):
        """Revoke certificate."""
        self.status = self.StatusChoices.REVOKED
        self.verification_status = f'revoked: {reason}'
        self.save()
