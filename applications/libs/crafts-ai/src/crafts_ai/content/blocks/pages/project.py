import logging

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock

logger = logging.getLogger(__name__)

__all__ = ["ProjectBlock"]


class ProjectBlock(BaseBlock):
    """
    Enhanced block for portfolio projects with rich features.
    """

    name = blocks.CharBlock(label=_("Project Name"), help_text=_("Name of the project"))

    description = blocks.RichTextBlock(
        label=_("Description"),
        help_text=_("Detailed description of the project"),
        features=["bold", "italic", "link", "ol", "ul"],
    )

    short_description = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Short Description"),
        help_text=_("Brief summary for project cards"),
    )

    thumbnail = ImageChooserBlock(
        required=False, label=_("Thumbnail Image"), help_text=_("Project thumbnail image")
    )

    technologies = blocks.ListBlock(
        blocks.CharBlock(label=_("Technology")),
        label=_("Technologies Used"),
        required=False,
        help_text=_("Technologies, frameworks, and tools used"),
    )

    project_url = blocks.URLBlock(
        required=False, label=_("Live Project URL"), help_text=_("Link to the live project")
    )

    github_url = blocks.URLBlock(
        required=False, label=_("GitHub Repository"), help_text=_("Link to source code repository")
    )

    start_date = blocks.DateBlock(label=_("Start Date"), help_text=_("When the project started"))

    end_date = blocks.DateBlock(
        required=False, label=_("End Date"), help_text=_("When the project ended (if applicable)")
    )

    is_ongoing = blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Ongoing Project"),
        help_text=_("Project is currently in development"),
    )

    is_featured = blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Featured Project"),
        help_text=_("Highlight this project as featured"),
    )

    project_type = blocks.ChoiceBlock(
        choices=[
            ("personal", _("Personal Project")),
            ("professional", _("Professional Work")),
            ("open_source", _("Open Source")),
            ("client", _("Client Project")),
            ("academic", _("Academic")),
        ],
        default="personal",
        label=_("Project Type"),
    )

    class Meta:
        label = _("Project")
        icon = "doc-full"
