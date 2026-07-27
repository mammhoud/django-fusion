from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock

from ..base import BaseBlock

__all__ = ["EnhancedEmbedBlock"]


class EnhancedEmbedBlock(BaseBlock):
    """
    Enhanced embed block with styling and responsive options.
    """

    embed_url = WagtailEmbedBlock(
        required=True,
        label=_("Embed URL"),
        help_text=_("URL to embed (YouTube, Vimeo, Twitter, etc.)."),
    )

    caption = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Caption"),
        help_text=_("Optional caption below the embed."),
    )

    max_width = blocks.CharBlock(
        required=False,
        default="100%",
        max_length=20,
        label=_("Maximum Width"),
        help_text=_("Maximum width of the embed (e.g., 800px, 100%, 50vw)."),
    )

    alignment = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("left", _("Left")),
            ("center", _("Center")),
            ("right", _("Right")),
        ],
        default="center",
        label=_("Alignment"),
    )

    responsive = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Responsive"),
        help_text=_("Make the embed responsive (adjust to container width)."),
    )

    lazy_load = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Lazy Load"),
        help_text=_("Delay loading the embed until it's visible."),
    )

    class Meta:
        icon = "media"
        label = _("Embed")
        group = _("Media")
