from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from ..base import BaseBlock


class ParagraphBlock(blocks.StructBlock):
    """
     paragraph block with rich text and styling.
    """
    
    content = blocks.RichTextBlock(
        required=True,
        label=_("Content"),
        features=['h2', 'h3', 'h4', 'bold', 'italic', 'link', 'code', 'superscript', 
                 'subscript', 'strikethrough', 'blockquote', 'ul', 'ol', 'hr', 
                 'document-link', 'image', 'embed'],
        help_text=_("Enter rich text content."),
    )
    
    alignment = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('left', _('Left Justified')),
            ('center', _('Center Aligned')),
            ('right', _('Right Justified')),
            ('justify', _('Full Justify')),
        ],
        default='left',
        label=_("Text Alignment"),
    )
    
    drop_cap = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Drop Cap"),
        help_text=_("Apply a drop cap to the first letter."),
    )
    
    background_color = blocks.CharBlock(
        required=False,
        max_length=20,
        label=_("Background Color"),
        help_text=_("Optional background color for the paragraph."),
    )
    
    text_color = blocks.CharBlock(
        required=False,
        max_length=20,
        label=_("Text Color"),
        help_text=_("Optional custom text color."),
    )
    
    padding = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('none', _('No Padding')),
            ('small', _('Small Padding')),
            ('medium', _('Medium Padding')),
            ('large', _('Large Padding')),
        ],
        default='none',
        label=_("Padding"),
    )
    
    class Meta:
        icon = "pilcrow"
        label = _(" Paragraph")
        group = _("Content")

