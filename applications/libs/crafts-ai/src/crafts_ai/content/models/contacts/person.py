from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.search import index

from ..default import DefaultBase
from .contact import ProfessionalBase

# =============================================================================
# PROFILE BASE (WAGTAIL INTEGRATED)
# =============================================================================


class PeopleBase(
    ProfessionalBase,
    index.Indexed,
    DefaultBase
):
    """
    Abstract base model for profile features with Wagtail CMS integration.
    Provides rich profile capabilities with media and social links.
    """

    profile_image = models.ImageField(
        _("Profile Image"),
        upload_to="profiles/%Y/%m/%d/",
        null=True,
        blank=True,
        default="profiles/default-avatar.png",
        help_text=_("Profile picture (recommended: 400x400px, square format)"),
    )

    cover_image = models.ImageField(
        _("Cover Image"),
        upload_to="profile_covers/%Y/%m/%d/",
        null=True,
        blank=True,
        default="profiles/default-cover.jpg",
        help_text=_("Cover image for profile header (recommended: 1200x400px)"),
    )

    bio = models.TextField(
        blank=True,
        verbose_name=_("Biography"),
        help_text=_("A comprehensive biography or professional summary"),
    )

    primary_website = models.URLField(
        blank=True,
        verbose_name=_("Primary Website"),
        help_text=_("Main website or company profile."),
    )

    class Meta:
        abstract = True
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    search_fields = [
        index.SearchField("bio"),
        index.SearchField("full_name", boost=2),
        index.SearchField("contact_methods"),
    ]

    @property
    def has_profile_image(self):
        """Check if profile has a custom image (not default)."""
        return (
            bool(self.profile_image)
            and self.profile_image.name != "profiles/default-avatar.png"
        )

    @property
    def has_cover_image(self):
        """Check if profile has a custom cover image (not default)."""
        return (
            bool(self.cover_image)
            and self.cover_image.name != "profiles/default-cover.jpg"
        )

    def clean(self):
        """Validate profile data."""
        super().clean()
