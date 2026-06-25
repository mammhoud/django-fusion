from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from ..contact import ContactMethodBlock, ContactProfileBlock
from ..pages import ProjectBlock, TestimonialBlock
from ..partials import (
    CertificationBlock,
)

# =============================================================================
# STREAM BLOCK CONTAINERS
# =============================================================================

__all__ = ["ProfileStreamBlock"]


class ProfileStreamBlock(blocks.StreamBlock):
    """
    Main stream block for profile content with enhanced features.
    """

    certification = CertificationBlock()
    project = ProjectBlock()
    testimonial = TestimonialBlock()
    contact_method = ContactMethodBlock()
    website_link = ContactProfileBlock(template="components/blocks/contact/contact_profile.html")

    class Meta:
        label = _("Profile Content")
        icon = "user"
        block_counts = {
            "certification": {"max_num": 25},
            "project": {"max_num": 20},
            "testimonial": {"max_num": 10},
            "contact_method": {"max_num": 10},
            "website_link": {"max_num": 10},
        }
