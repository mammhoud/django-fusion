from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from ..base import BaseBlock


class HTMLBlock(BaseBlock):
    """
     HTML block with security and styling options.
    """
    
    html_content = blocks.RawHTMLBlock(
        required=True,
        label=_("HTML Content"),
        help_text=_("Enter custom HTML, CSS, or JavaScript."),
    )
    
    sanitize_html = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Sanitize HTML"),
        help_text=_("Remove potentially dangerous HTML tags and attributes."),
    )
    
    allow_scripts = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Allow JavaScript"),
        help_text=_("Allow JavaScript execution (use with caution)."),
    )
    
    allow_styles = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Allow CSS Styles"),
        help_text=_("Allow inline CSS styles."),
    )
    
    container = blocks.ChoiceBlock(
        required=False,
        choices=[
            ('none', _('No Container')),
            ('div', _('Div Container')),
            ('section', _('Section Container')),
            ('article', _('Article Container')),
        ],
        default='div',
        label=_("HTML Container"),
    )
    
    class Meta:
        icon = "code"
        label = _(" HTML")
        group = _("Advanced")

