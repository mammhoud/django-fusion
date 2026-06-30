import logging

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator, validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _
from ceptor_ai.content.blocks.contact.stream_blocks import ContactMethodsStreamBlock
from modelcluster.models import ClusterableModel
from wagtail.fields import StreamField

logger = logging.getLogger(__name__)

PHONE_VALIDATOR = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_(
        "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    ),
)


# =============================================================================
# CONTACT BASE
# =============================================================================


class ContactBase(ClusterableModel):
    """
    Abstract base model providing core contact fields and validation.
    """

    full_name = models.CharField(
        max_length=100,
        verbose_name=_("Full Name"),
    )

    email = models.EmailField(
        verbose_name=_("Email Address"),
        blank=True,
        help_text=_("Primary email address"),
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[PHONE_VALIDATOR],
        verbose_name=_("Phone Number"),
        help_text=_("Format: +999999999 (up to 15 digits)."),
    )

    # StreamField for flexible contact methods
    contact_methods = StreamField(
        ContactMethodsStreamBlock,
        blank=True,
        verbose_name=_("Additional Contact Methods"),
        help_text=_("Add email, phone, social media, and website contacts"),
        use_json_field=True,
    )

    class Meta:
        abstract = True
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["full_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    # ---------------------- Computed Properties ----------------------

    @property
    def initials(self) -> str:
        """Return initials (uppercase)."""
        first = self.full_name[:1].upper() if self.full_name else ""
        last = (
            self.full_name.split(" ")[-1][:1].upper()
            if self.full_name and " " in self.full_name
            else ""
        )
        return f"{first}{last}"

    # ---------------------- StreamField Contact Methods Properties ----------------------

    @property
    def all_contact_methods(self) -> list[dict]:
        """Get all contact methods from StreamField."""
        methods = []
        for block in self.contact_methods:
            if block.block_type == "contact_method":
                methods.append(
                    {
                        "type": "contact_method",
                        "contact_type": block.value.get("contact_type"),
                        "value": block.value.get("value"),
                        "label": block.value.get("label"),
                        "is_primary": block.value.get("is_primary", False),
                        "verified": block.value.get("verified", False),
                        "notes": block.value.get("notes", ""),
                        "block_id": block.id,
                    }
                )
        return methods

    @property
    def social_media_profiles(self) -> list[dict]:
        """Get all social media profiles from StreamField."""
        profiles = []
        for block in self.contact_methods:
            if block.block_type == "social_media":
                profiles.append(
                    {
                        "type": "social_media",
                        "platform": block.value.get("platform"),
                        "platform_display": block.value.get(
                            "platform_display", block.value.get("platform")
                        ),
                        "username": block.value.get("username"),
                        "profile_url": block.value.get("profile_url"),
                        "is_primary": block.value.get("is_primary", False),
                        "is_public": block.value.get("is_public", True),
                        "verified": block.value.get("verified", False),
                        "notes": block.value.get("notes", ""),
                        "block_id": block.id,
                    }
                )
        return profiles

    @property
    def website_links(self) -> list[dict]:
        """Get all website links from StreamField."""
        links = []
        for block in self.contact_methods:
            if block.block_type == "website_link":
                links.append(
                    {
                        "type": "website_link",
                        "url": block.value.get("url"),
                        "title": block.value.get("title"),
                        "website_type": block.value.get("website_type"),
                        "is_primary": block.value.get("is_primary", False),
                        "description": block.value.get("description", ""),
                        "show_in_directory": block.value.get("show_in_directory", True),
                        "block_id": block.id,
                    }
                )
        return links

    @property
    def primary_email(self) -> str | None:
        """Get primary email address."""
        # First check direct field
        if self.email:
            return self.email

        # Then check contact methods in StreamField
        for method in self.all_contact_methods:
            if method.get("contact_type") == "email" and method.get("is_primary"):
                return method.get("value")

        return None

    @property
    def primary_phone(self) -> str | None:
        """Get primary phone number."""
        # First check direct fields
        if self.phone:
            return self.phone

        # Then check contact methods in StreamField
        for method in self.all_contact_methods:
            if method.get("contact_type") in ["phone"] and method.get("is_primary"):
                return method.get("value")

        return None

    @property
    def verified_contact_methods(self) -> list[dict]:
        """Get all verified contact methods."""
        verified = []

        # Check direct fields
        if self.email and self.email_verified:
            verified.append(
                {
                    "type": "email",
                    "value": self.email,
                    "source": "direct_field",
                    "verified": True,
                }
            )

        # Check StreamField methods
        for method in self.all_contact_methods:
            if method.get("verified"):
                verified.append(method)

        for profile in self.social_media_profiles:
            if profile.get("verified"):
                verified.append(profile)

        return verified

    def get_contact_methods_by_type(self, contact_type: str) -> list[dict]:
        """Get contact methods by type from StreamField."""
        return [
            method
            for method in self.all_contact_methods
            if method.get("contact_type") == contact_type
        ]

    def get_social_profiles_by_platform(self, platform: str) -> list[dict]:
        """Get social media profiles by platform."""
        return [
            profile
            for profile in self.social_media_profiles
            if profile.get("platform") == platform
        ]

    def get_websites_by_type(self, website_type: str) -> list[dict]:
        """Get website links by type."""
        return [
            website
            for website in self.website_links
            if website.get("website_type") == website_type
        ]

    def add_contact_method(self, contact_type: str, value: str, **kwargs):
        """Programmatically add a contact method to StreamField."""
        from wagtail.blocks import StreamValue

        # Create new contact method block
        new_block = {
            "type": "contact_method",
            "value": {
                "contact_type": contact_type,
                "value": value,
                "label": kwargs.get("label", ""),
                "is_primary": kwargs.get("is_primary", False),
                "verified": kwargs.get("verified", False),
                "notes": kwargs.get("notes", ""),
            },
        }

        # Add to existing StreamField data
        current_data = list(self.contact_methods.stream_data)
        current_data.append(new_block)

        # Update StreamField
        self.contact_methods = StreamValue(
            self.contact_methods.stream_block, current_data
        )
        self.save()

    # ---------------------- Validation ----------------------

    def clean(self):
        super().clean()

        # Require at least one contact method
        if not self.email and not self.phone and not self.contact_methods:
            raise ValidationError(
                _("At least one contact method (email or phone) is required.")
            )

        # Validate StreamField contact methods
        self._validate_streamfield_contact_methods()

    def _validate_streamfield_contact_methods(self):
        """Validate contact methods in StreamField."""
        for block in self.contact_methods:
            block_value = block.value

            if block.block_type == "contact_method":
                contact_type = block_value.get("contact_type")
                value = block_value.get("value", "")

                if contact_type == "email":
                    try:
                        validate_email(value)
                    except ValidationError:
                        raise ValidationError(
                            {
                                "contact_methods": _(
                                    "Invalid email address in contact methods: %(value)s"
                                )
                                % {"value": value}
                            }
                        )

                elif contact_type in ["phone"]:
                    try:
                        PHONE_VALIDATOR(value)
                    except ValidationError:
                        raise ValidationError(
                            {
                                "contact_methods": _(
                                    "Invalid phone number format in contact methods: %(value)s"
                                )
                                % {"value": value}
                            }
                        )

                elif contact_type in ["website", "social"]:
                    validator = URLValidator()
                    try:
                        validator(value)
                    except ValidationError:
                        raise ValidationError(
                            {
                                "contact_methods": _(
                                    "Invalid URL in contact methods: %(value)s"
                                )
                                % {"value": value}
                            }
                        )

            elif block.block_type == "website_link":
                url = block_value.get("url", "")
                validator = URLValidator()
                try:
                    validator(url)
                except ValidationError:
                    raise ValidationError(
                        {
                            "contact_methods": _("Invalid website URL: %(url)s")
                            % {"url": url}
                        }
                    )

    def __str__(self) -> str:
        return self.full_name
