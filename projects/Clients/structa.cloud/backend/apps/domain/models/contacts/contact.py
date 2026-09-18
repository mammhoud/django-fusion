import logging

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base import ContactBase

logger = logging.getLogger(__name__)


# =============================================================================
# PROFESSIONAL BASE
# =============================================================================

class ProfessionalBase(ContactBase):
    """
    Abstract base model for professional and organizational relationships.
    """

    job_title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Job Title"),
    )

    organization = models.ForeignKey(
        "handlers.company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_related",
        verbose_name=_("Organization"),
        help_text=_("Primary organization or company."),
    )

    department = models.ForeignKey(
        "handlers.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_related",
        verbose_name=_("Department"),
        help_text=_("Department within the organization."),
    )

    # Contact verification flags
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_("Email Verified"),
    )


    class Meta:
        app_label = "shared"
        abstract = True
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["department"]),
            models.Index(fields=["job_title"]),
        ]

    # ---------------------- Properties ----------------------

    @property
    def is_current(self) -> bool:
        """Return whether this professional relationship is active."""
        today = timezone.now().date()
        if self.start_date and self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True

    @property
    def professional_title(self) -> str:
        """Return formatted professional title."""
        title = self.job_title or _("Professional")
        if self.organization:
            return f"{title} at {self.organization.name}"
        return title

    # ---------------------- Contact Methods Enhancement ----------------------

    @property
    def primary_contact_methods(self) -> list[dict]:
        """Get all primary contact methods."""
        return [contact for contact in self.all_contact_points if contact.get('is_primary')]

    @property
    def public_contact_methods(self) -> list[dict]:
        """Get all public contact methods."""
        public_contacts = []

        for contact in self.all_contact_points:
            if contact.get('type') == 'social_media':
                if contact.get('is_public', True):
                    public_contacts.append(contact)
            elif contact.get('type') == 'website_link':
                if contact.get('show_in_directory', True):
                    public_contacts.append(contact)
            else:
                public_contacts.append(contact)

        return public_contacts

    # ---------------------- Save Logic ----------------------

    def __str__(self) -> str:
        return f"{self.full_name} — {self.professional_title}"

