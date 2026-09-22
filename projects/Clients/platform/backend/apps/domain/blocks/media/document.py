from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock

from ..base import BaseBlock


class DocumentBlock(BaseBlock):
    """
     document block with download options and styling.
    """
    
    document = DocumentChooserBlock(
        required=True,
        label=_("Document"),
        help_text=_("Select a document to display."),
    )
    
    title = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Custom Title"),
        help_text=_("Override the document's filename as the display title."),
    )
    
    description = blocks.TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Optional description of the document."),
    )
    
    show_icon = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show File Icon"),
    )
    
    show_size = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show File Size"),
    )
    
    show_download_count = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Download Count"),
    )
    
    button_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('link', _('Text Link')),
            ('button', _('Button')),
            ('card', _('Card')),
            ('inline', _('Inline Badge')),
        ],
        default='button',
        label=_("Display Style"),
    )
    
    button_text = blocks.CharBlock(
        required=False,
        default=_("Download"),
        max_length=50,
        label=_("Button Text"),
    )
    
    class Meta:
        icon = "doc-full"
        label = _(" Document")
        group = _("Content")

