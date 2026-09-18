from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import PageChooserBlock

from ..base import BaseBlock


class PageLinkBlock(BaseBlock):
    """
    A reusable block allowing editors to select an internal page,
    customize link text, and optionally include an icon class.

    Ideal for call-to-action buttons, card links, or navigation items.
    """

    page = PageChooserBlock(
        required=True,
        help_text=_("Select an internal page to link to."),
    )

    link_text = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text=_("Text displayed for the link (defaults to page title if empty)."),
    )

    icon = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text=_("Optional icon class (e.g., 'fa fa-arrow-right', 'bi bi-link-45deg')."),
    )

    open_in_new_tab = blocks.BooleanBlock(
        required=False,
        help_text=_("Open the link in a new tab."),
    )

    class Meta:
        icon = "link"
        label = _("Page Link")
        help_text = _("A link with optional text and icon pointing to an internal page.")
