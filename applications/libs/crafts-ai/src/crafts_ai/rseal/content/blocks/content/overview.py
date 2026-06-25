from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from ..partials.tables import TableBlock, TypedTableSectionBlock
from ..profile import InfoSectionBlock
from .quote import BlockQuote


class OverviewBlock(blocks.StreamBlock):
    """
    A versatile section for overviews — used in About, and Course pages.
    """

    heading = blocks.CharBlock(
        icon="title",
        label=_("Heading"),
        help_text=_("Main heading for this section."),
        # template was: blocks/heading_block.html,
    )

    paragraph = blocks.RichTextBlock(
        icon="pilcrow",
        label=_("Paragraph"),
        features=["h2", "h3", "bold", "italic", "link", "ol", "ul", "code"],
        # template was: blocks/paragraph_block.html,
    )

    image = ImageChooserBlock(
        icon="image",
        label=_("Image"),
        help_text=_("Optional image for this section."),
        # template was: blocks/image_block.html,
    )

    quote = BlockQuote(template="components/blocks/content/block_quote.html")

    embed = EmbedBlock(
        icon="media",
        label=_("Embedded Video/Media"),
        help_text=_("Embed a video or external media (YouTube, Vimeo, etc.)"),
        # template was: blocks/embed_block.html,
    )

    table = TableBlock(label=_("Table"), template="components/blocks/partials/enhanced_table.html",
        # template was: blocks/table_block.html,
    )

    typed_table = TypedTableSectionBlock(
        [
            ("text", blocks.CharBlock(label=_("Text"))),
            ("number", blocks.FloatBlock(label=_("Number"))),
            ("rich_text", blocks.RichTextBlock(label=_("Rich Text"))),
            ("file", blocks.CharBlock(label=_("File Link"))),
        ],
        label=_("Typed Table"),
        # template was: blocks/typed_table.html,
    )

    info_section = InfoSectionBlock()

    class Meta:
        icon = "doc-full"
        label = _("Overview Content")
        help_text = _("Flexible content for overview sections.")
        block_counts = {
            "heading": {"max_num": 3},
            "quote": {"max_num": 2},
            "embed": {"max_num": 3},
        }
