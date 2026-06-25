import logging
from datetime import date

from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from ..base import BaseBlock

logger = logging.getLogger(__name__)

__all__ = ["CertificationBlock"]


class CertificationBlock(BaseBlock):
    """
    Enhanced block for professional certifications with verification.
    """

    name = blocks.CharBlock(
        label=_("Certification Name"), help_text=_("Full name of the certification")
    )

    issuing_organization = blocks.CharBlock(
        label=_("Issuing Organization"), help_text=_("Organization that issued the certification")
    )

    issue_date = blocks.DateBlock(
        label=_("Issue Date"), help_text=_("When the certification was issued")
    )

    expiration_date = blocks.DateBlock(
        required=False,
        label=_("Expiration Date"),
        help_text=_("When the certification expires (if applicable)"),
    )

    credential_id = blocks.CharBlock(
        required=False,
        label=_("Credential ID"),
        help_text=_("Official credential or license number"),
    )

    credential_url = blocks.URLBlock(
        required=False,
        label=_("Credential URL"),
        help_text=_("Link to verify the credential online"),
    )

    skills = blocks.ListBlock(
        blocks.CharBlock(label=_("Skill")),
        label=_("Related Skills"),
        required=False,
        help_text=_("Skills demonstrated by this certification"),
    )

    is_expired = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Expired"),
        help_text=_("Mark if certification has expired"),
    )

    show_badge = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Badge"),
        help_text=_("Display certification badge"),
    )

    class Meta:
        label = _("Certification")
        icon = "success"

    def clean(self, value):
        cleaned_data = super().clean(value)

        # Auto-detect if expired
        expiration_date = cleaned_data.get("expiration_date")
        if expiration_date:
            cleaned_data["is_expired"] = expiration_date < date.today()

        return cleaned_data
