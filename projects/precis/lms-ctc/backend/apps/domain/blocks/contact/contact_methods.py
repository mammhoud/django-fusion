import logging

from django.utils.translation import gettext_lazy as _
from wagtail import blocks

logger = logging.getLogger(__name__)

__all__ = ["ContactMethodBlock"]


class ContactMethodBlock(blocks.StructBlock):
    """
    Enhanced block for contact methods with type, value, and verification.
    """

    CONTACT_TYPE_CHOICES = [
        ("email", _("Email Address")),
        ("phone", _("Phone Number")),
        ("mobile", _("Mobile Phone")),
        ("fax", _("Fax Number")),
        ("website", _("Website")),
        ("social", _("Social Media")),
        ("address", _("Physical Address")),
        ("other", _("Other")),
    ]

    contact_type = blocks.ChoiceBlock(
        choices=CONTACT_TYPE_CHOICES,
        default="email",
        label=_("Contact Type"),
        help_text=_("Type of contact method"),
    )

    value = blocks.CharBlock(
        max_length=255,
        required=True,
        label=_("Contact Value"),
        help_text=_("Email address, phone number, URL, username, etc."),
    )

    label = blocks.CharBlock(
        max_length=100,
        required=False,
        label=_("Custom Label"),
        help_text=_("Optional custom label for this contact method"),
    )

    is_primary = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Primary Contact"),
        help_text=_("Mark as the primary contact method for this type"),
    )

    verified = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Verified"),
        help_text=_("Has this contact method been verified?"),
    )

    show_publicly = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Publicly"),
        help_text=_("Display this contact method publicly"),
    )

    icon_class = blocks.CharBlock(
        required=False,
        label=_("Icon CSS Class"),
        help_text=_("Optional CSS class for custom icons"),
    )

    notes = blocks.TextBlock(
        required=False,
        label=_("Notes"),
        help_text=_("Additional notes or context for this contact method"),
    )

    class Meta:
        label = _("Contact Method")
        icon = "phone"
        form_classname = "contact-method-block"

    def clean(self, value):
        cleaned_data = super().clean(value)

        # Auto-generate label if not provided
        if not cleaned_data.get("label"):
            contact_type = cleaned_data.get("contact_type", "")
            type_display = dict(self.CONTACT_TYPE_CHOICES).get(contact_type, _("Contact"))
            cleaned_data["label"] = f"{type_display}"

        # Auto-set icon class if not provided
        if not cleaned_data.get("icon_class"):
            icon_map = {
                "email": "bi bi-envelope",
                "phone": "bi bi-telephone",
                "mobile": "bi bi-phone",
                "fax": "bi bi-printer",
                "website": "bi bi-globe",
                "social": "bi bi-share",
                "address": "bi bi-geo-alt",
                "other": "bi bi-link",
            }
            cleaned_data["icon_class"] = icon_map.get(contact_type, "bi bi-link")

        return cleaned_data
