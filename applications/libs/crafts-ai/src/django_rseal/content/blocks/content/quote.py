"""
 quote and testimonial blocks.
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock


class BlockQuote(blocks.StructBlock):
    """
     block quote with citation and styling options.
    """
    
    quote_text = blocks.TextBlock(
        required=True,
        label=_("Quote Text"),
        help_text=_("The quoted text."),
    )
    
    citation = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Citation"),
        help_text=_("Who said it (e.g., 'John Doe, CEO of Company')."),
    )
    
    citation_url = blocks.URLBlock(
        required=False,
        label=_("Citation URL"),
        help_text=_("Optional link for the citation."),
    )
    
    avatar = ImageChooserBlock(
        required=False,
        label=_("Avatar Image"),
        help_text=_("Optional photo of the person quoted."),
    )
    
    # Styling Options
    quote_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('default', _('Default')),
            ('large', _('Large Text')),
            ('border', _('With Border')),
            ('icon', _('With Quote Icon')),
            ('highlight', _('Highlighted Background')),
        ],
        default='default',
        label=_("Quote Style"),
    )
    
    alignment = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('left', _('Left Aligned')),
            ('center', _('Center Aligned')),
            ('right', _('Right Aligned')),
        ],
        default='left',
        label=_("Alignment"),
    )
    
    # Icon Options
    quote_icon = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Quote Icon"),
    )
    
    icon_position = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('top-left', _('Top Left')),
            ('top', _('Top Center')),
            ('left', _('Left Side')),
        ],
        default='top-left',
        label=_("Icon Position"),
    )
    
    class Meta:
        icon = "openquote"
        label = _("Block Quote")
        # template was: blocks/block_quote.html
        group = _("Content")
    
    def get_quote_classes(self, value):
        """Get CSS classes for the quote block."""
        classes = ['block-quote']
        
        # Style classes
        style = value.get('quote_style', 'default')
        if style != 'default':
            classes.append(f'block-quote--{style}')
        
        # Alignment classes
        alignment = value.get('alignment', 'left')
        if alignment == 'center':
            classes.append('text-center')
        elif alignment == 'right':
            classes.append('text-end')
        
        # Icon position classes
        if value.get('quote_icon', True):
            icon_pos = value.get('icon_position', 'top-left')
            classes.append(f'has-icon--{icon_pos}')
        
        return ' '.join(classes)

