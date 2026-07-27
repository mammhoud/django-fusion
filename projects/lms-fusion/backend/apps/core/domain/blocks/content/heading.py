from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from ..base import BaseBlock


class AdvancedHeadingBlock(BaseBlock):
    """
    heading block with styling options.
    """

    text = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Heading Text"),
        help_text=_("Enter the heading text."),
    )

    level = blocks.ChoiceBlock(
        required=True,
        choices=[
            ("h1", "H1"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
            ("h5", "H5"),
            ("h6", "H6"),
        ],
        default="h2",
        label=_("Heading Level"),
    )

    alignment = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("left", _("Left")),
            ("center", _("Center")),
            ("right", _("Right")),
        ],
        default="left",
        label=_("Text Alignment"),
    )

    show_divider = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Divider Line"),
        help_text=_("Add a decorative line below the heading."),
    )

    divider_color = blocks.CharBlock(
        required=False,
        max_length=20,
        default="#3b82f6",
        label=_("Divider Color"),
        help_text=_("CSS color for the divider line."),
    )

    icon = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Icon Class"),
        help_text=_("Optional icon to display before heading (e.g., 'fas fa-star')."),
    )

    class Meta:
        icon = "title"
        label = _(" Heading")
        group = _("Content")
