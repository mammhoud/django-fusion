import logging

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock
from .contact_methods import ContactMethodBlock
from .website_links import ContactProfileBlock

logger = logging.getLogger(__name__)

__all__ = ["ContactCardBlock"]


class ContactCardBlock(BaseBlock):
    """
    Enhanced contact section with background, multiple contact methods, and form options.
    """

    background_image = ImageChooserBlock(
        required=False, help_text=_("Background image for the contact section")
    )

    background_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("none", _("No Background")),
            ("image", _("Background Image")),
            ("gradient", _("Gradient")),
            ("pattern", _("Pattern")),
        ],
        default="none",
        label=_("Background Style"),
    )

    subtitle = blocks.CharBlock(
        max_length=100, required=False, help_text=_("Small title or intro text")
    )

    title = blocks.CharBlock(max_length=200, required=True, help_text=_("Main heading"))

    description = blocks.RichTextBlock(
        required=False,
        help_text=_("Optional description text"),
        features=["bold", "italic", "link"],
    )

    contact_methods = blocks.StreamBlock(
        [
            ("contact", ContactMethodBlock()),
            ("website", ContactProfileBlock(template="components/blocks/contact/contact_profile.html")),
        ],
        required=False,
        label=_("Contact Methods"),
        help_text=_("Add multiple contact methods"),
    )

    show_contact_form = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Contact Form"),
        help_text=_("Display a contact form in this section"),
    )

    form_title = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Form Title"),
        help_text=_("Title for the contact form section"),
    )

    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("split", _("Split Layout")),
            ("stacked", _("Stacked Layout")),
            ("cards", _("Cards Layout")),
            ("compact", _("Compact Layout")),
        ],
        default="split",
        label=_("Layout Style"),
    )

    class Meta:
        icon = "mail"
        label = _("Contact Section")
