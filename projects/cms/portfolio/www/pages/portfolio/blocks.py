"""
Portfolio Blocks - Reusable content blocks for portfolio models
"""
from django.utils.translation import gettext_lazy as _
from wagtail.images.blocks import ImageChooserBlock
from wagtail import blocks


class ProjectBlock(blocks.StructBlock):
    """
    📁 Project block for portfolio section with enhanced content.
    """
    title = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Title"),
        help_text=_("Project title"),
    )
    category = blocks.CharBlock(
        max_length=100,
        required=True,
        label=_("Category"),
        help_text=_("Project category (e.g., Web Development, Design)"),
    )
    image = ImageChooserBlock(
        required=False,
        label=_("Image"),
        help_text=_("Project thumbnail image"),
        template="blocks/media/image_lite.html",
    )
    description = blocks.TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Brief description of the project"),
    )
    content = blocks.RichTextBlock(
        required=False,
        label=_("Content"),
        help_text=_("Detailed content/description of the project"),
    )
    video_url = blocks.URLBlock(
        required=False,
        label=_("Video URL"),
        help_text=_("Link to project video (YouTube, Vimeo, etc.)"),
    )
    tools = blocks.ListBlock(
        blocks.CharBlock(max_length=100),
        required=False,
        label=_("Tools & Technologies"),
        help_text=_("List of tools and technologies used in this project"),
    )
    tags = blocks.ListBlock(
        blocks.CharBlock(max_length=100),
        required=False,
        label=_("Tags"),
        help_text=_("List of tags for this project"),
    )
    url = blocks.URLBlock(
        required=False,
        label=_("Project URL"),
        help_text=_("Link to the project"),
    )

    class Meta:
        template = "portfolio/blocks/project.html"
        icon = "folder"
        label = _("Project")
