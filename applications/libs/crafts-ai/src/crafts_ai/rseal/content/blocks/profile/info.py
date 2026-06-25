from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class InfoSectionBlock(blocks.StructBlock):
    """
    Flexible section for structured content (overview, details, FAQ, etc.)
    """

    SECTION_CHOICES = [
        ("overview", _("Overview")),
        ("details", _("Details")),
        ("requirements", _("Requirements")),
        ("resources", _("Resources")),
    ]

    section_type = blocks.ChoiceBlock(
        choices=SECTION_CHOICES,
        label=_("Section Type"),
        required=False,
        help_text=_("Defines what kind of section this is."),
    )

    heading = blocks.CharBlock(
        required=False,
        label=_("Heading"),
        help_text=_("Optional heading for the section."),
    )

    body = blocks.RichTextBlock(
        required=False,
        label=_("Body Text"),
        features=["h2", "h3", "bold", "italic", "link", "ol", "ul", "code"],
        help_text=_("Main descriptive text for this section."),
    )

    image = ImageChooserBlock(
        required=False,
        label=_("Image"),
        help_text=_("Optional image for this section."),
    )

    embed = EmbedBlock(
        required=False,
        label=_("Embedded Media"),
        help_text=_("Insert a YouTube/Vimeo or other embed URL."),
    )

    list_items = blocks.ListBlock(
        blocks.CharBlock(label=_("List Item")),
        required=False,
        label=_("Key Points"),
    )

    class Meta:
        icon = "folder-open-inverse"
        label = _("Information Section")
        help_text = _("A flexible structured information block for use in pages.")
