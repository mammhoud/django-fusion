from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock


class HeadingBlock(BaseBlock):
    """
    Simple heading block for consistent typography.
    """

    text = blocks.CharBlock(required=True, label=_("Heading Text"))
    size = blocks.ChoiceBlock(
        choices=[
            ("h2", _("H2 – Section Heading")),
            ("h3", _("H3 – Subheading")),
            ("h4", _("H4 – Small Heading")),
        ],
        default="h2",
        label=_("Heading Size"),
    )

    class Meta:
        icon = "title"
        label = _("Heading")
        # template was: blocks/heading_block.html


class PageTitleSectionBlock(blocks.StructBlock):
    """
    A block representing a page header section with optional background image
    and breadcrumb home text.
    """

    page_title_background = ImageChooserBlock(
        required=False,
        help_text=_("Optional background image for the page title section."),
    )
    page_title = blocks.CharBlock(
        required=True,
        max_length=200,
        help_text=_("The main heading displayed in the page title section."),
    )
    breadcrumb_home_text = blocks.CharBlock(
        default=_("Home"),
        max_length=50,
        help_text=_("The label used for the breadcrumb home link."),
    )

    class Meta:
        icon = "image"
        label = _("Page Title Section")
        help_text = _("A section for page title with optional background and breadcrumb text.")
