from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from .contact.stream_blocks import ContactMethodsStreamBlock
from .content.heading import AdvancedHeadingBlock
from .content.paragraph import ParagraphBlock
from .content.quote import BlockQuote
from .media.document import DocumentBlock
from .media.embed import EnhancedEmbedBlock
from .media.image import ImageBlock
from .media.video import VideoBlock
from .profile.stream_blocks import ProfileStreamBlock

__all__ = [
    "BaseStreamBlock",
    "ContactMethodsStreamBlock",
    "ProfileStreamBlock",
]


class BaseStreamBlock(blocks.StreamBlock):
    """
    General-purpose StreamBlock used as the default block set for StreamFields
    such as blog post body and class materials. Combines common content and
    media blocks.
    """

    heading = AdvancedHeadingBlock()
    paragraph = ParagraphBlock()
    block_quote = BlockQuote()
    image = ImageBlock()
    video = VideoBlock()
    document = DocumentBlock()
    embed = EnhancedEmbedBlock()

    class Meta:
        icon = "placeholder"
        label = _("Base Stream Block")

