import logging

from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from .contact_methods import ContactMethodBlock

logger = logging.getLogger(__name__)

__all__ = ["ContactMethodsStreamBlock"]


class ContactMethodsStreamBlock(blocks.StreamBlock):
    """
    StreamBlock container for all contact method types.
    """

    contact_method = ContactMethodBlock()

    class Meta:
        label = _("Contact Methods")
        icon = "phone"
        block_counts = {
            "contact_method": {"min_num": 0, "max_num": 20},
        }
