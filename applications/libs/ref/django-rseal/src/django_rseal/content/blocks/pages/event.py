"""
Event section blocks with schedules, speakers, and registration forms.
"""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock
from ..content.quote import BlockQuote
from ..media.image import ImageBlock, SimpleImageBlock
from ..media.video import VideoBlock

__all__ = ["EventSpeakerBlock", "EventScheduleItemBlock", "EventSectionBlock"]


class EventSpeakerBlock(BaseBlock):
    """
    Event speaker profile block.
    """

    name = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Speaker Name"),
    )

    title = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Speaker Title"),
        help_text=_("Position and company/organization."),
    )

    bio = blocks.RichTextBlock(
        required=False,
        label=_("Biography"),
        features=["bold", "italic", "link"],
    )

    photo = ImageChooserBlock(
        required=True,
        label=_("Speaker Photo"),
    )

    # Session Information
    session_title = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Session Title"),
    )

    session_time = blocks.CharBlock(
        required=False,
        max_length=50,
        label=_("Session Time"),
        help_text=_("e.g., '10:00 AM - 11:00 AM'"),
    )

    session_location = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Session Location"),
        help_text=_("Room name, stage, or virtual platform."),
    )

    # Social Links
    social_links = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "platform",
                    blocks.ChoiceBlock(
                        choices=[
                            ("linkedin", "LinkedIn"),
                            ("twitter", "Twitter/X"),
                            ("website", "Website"),
                            ("github", "GitHub"),
                            ("book", "Publications"),
                        ],
                        label=_("Platform"),
                    ),
                ),
                (
                    "url",
                    blocks.URLBlock(
                        required=True,
                        label=_("URL"),
                    ),
                ),
            ],
            label=_("Social Link"),
        ),
        required=False,
        label=_("Social Links"),
    )

    # Featured Status
    featured_speaker = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Featured Speaker"),
        help_text=_("Highlight as keynote or main speaker."),
    )

    class Meta:
        icon = "user"
        label = _("Event Speaker")
        # template was: blocks/event_speaker.html
        group = _("Events")


class EventScheduleItemBlock(BaseBlock):
    """
    Individual item in event schedule/timetable.
    """

    time = blocks.CharBlock(
        required=True,
        max_length=50,
        label=_("Time"),
        help_text=_("e.g., '9:00 AM - 10:00 AM'"),
    )

    title = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Session Title"),
    )

    description = blocks.RichTextBlock(
        required=False,
        label=_("Session Description"),
        features=["bold", "italic", "link"],
    )

    speaker = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Speaker(s)"),
        help_text=_("Name of presenter(s)."),
    )

    location = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Location"),
        help_text=_("Room, stage, or virtual location."),
    )

    session_type = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("keynote", _("Keynote")),
            ("workshop", _("Workshop")),
            ("panel", _("Panel Discussion")),
            ("breakout", _("Breakout Session")),
            ("networking", _("Networking")),
            ("break", _("Break")),
            ("meal", _("Meal")),
        ],
        default="keynote",
        label=_("Session Type"),
    )

    # Resources
    resources = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "type",
                    blocks.ChoiceBlock(
                        choices=[
                            ("slides", _("Presentation Slides")),
                            ("video", _("Recording")),
                            ("document", _("Document")),
                            ("link", _("External Link")),
                        ],
                        label=_("Resource Type"),
                    ),
                ),
                (
                    "title",
                    blocks.CharBlock(
                        required=True,
                        max_length=100,
                        label=_("Resource Title"),
                    ),
                ),
                (
                    "url",
                    blocks.URLBlock(
                        required=True,
                        label=_("Resource URL"),
                    ),
                ),
                (
                    "description",
                    blocks.CharBlock(
                        required=False,
                        max_length=200,
                        label=_("Description"),
                    ),
                ),
            ],
            label=_("Resource"),
        ),
        required=False,
        label=_("Session Resources"),
    )

    class Meta:
        icon = "time"
        label = _("Schedule Item")
        # template was: blocks/event_schedule_item.html
        group = _("Events")


class EventSectionBlock(BaseBlock):
    """
    event section with flexible content
    """

    # Event Information
    event_title = blocks.CharBlock(
        required=True,
        max_length=200,
        label=_("Event Title"),
    )

    event_date = blocks.DateBlock(
        required=False,
        label=_("Event Date"),
    )

    event_location = blocks.CharBlock(
        required=False,
        max_length=200,
        label=_("Event Location"),
        help_text=_("Physical or virtual location."),
    )

    event_description = blocks.RichTextBlock(
        required=False,
        label=_("Event Description"),
        features=["bold", "italic", "link", "h2", "h3", "ul", "ol"],
    )

    # Registration
    show_registration = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Registration"),
    )

    registration_title = blocks.CharBlock(
        required=False,
        default=_("Register Now"),
        max_length=200,
        label=_("Registration Title"),
    )

    registration_description = blocks.RichTextBlock(
        required=False,
        label=_("Registration Description"),
    )

    registration_url = blocks.URLBlock(
        required=False,
        label=_("Registration URL"),
    )

    registration_deadline = blocks.DateBlock(
        required=False,
        label=_("Registration Deadline"),
    )

    # Content Sections
    content_sections = blocks.StreamBlock(
        [
            (
                "heading",
                blocks.StructBlock(
                    [
                        (
                            "text",
                            blocks.CharBlock(
                                required=True,
                                max_length=200,
                                label=_("Heading Text"),
                            ),
                        ),
                        (
                            "level",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("h2", "H2"),
                                    ("h3", "H3"),
                                    ("h4", "H4"),
                                ],
                                default="h2",
                                label=_("Heading Level"),
                            ),
                        ),
                    ],
                    icon="title",
                    label=_("Section Heading"),
                ),
            ),
            (
                "paragraph",
                blocks.RichTextBlock(
                    features=["bold", "italic", "link", "ul", "ol"],
                    icon="pilcrow",
                    label=_("Paragraph"),
                ),
            ),
            (
                "image",
                SimpleImageBlock(label=_("Image"), template="components/blocks/media/simple_image.html",
                ),
            ),
            (
                "video",
                VideoBlock(label=_("Video"), template="components/blocks/media/enhanced_video.html",
                ),
            ),
            (
                "embed",
                EmbedBlock(
                    label=_("Embedded Media"),
                    help_text=_("Embed video, social media, or other content."),
                ),
            ),
            (
                "document",
                DocumentChooserBlock(
                    label=_("Document"),
                ),
            ),
            (
                "table",
                TableBlock(label=_("Table"), template="components/blocks/partials/enhanced_table.html",
                    help_text=_("Add structured data like schedules or pricing."),
                ),
            ),
            (
                "speaker",
                EventSpeakerBlock(label=_("Speaker Profile"), template="components/blocks/pages/event_speaker.html",
                ),
            ),
            (
                "schedule",
                EventScheduleItemBlock(label=_("Schedule Item"), template="components/blocks/pages/event_schedule_item.html",
                ),
            ),
            (
                "quote",
                BlockQuote(label=_("Quote"), template="components/blocks/content/block_quote.html",
                ),
            ),
            (
                "html",
                blocks.RawHTMLBlock(
                    label=_("Custom HTML"),
                    icon="code",
                ),
            ),
            (
                "sponsors",
                blocks.StructBlock(
                    [
                        (
                            "title",
                            blocks.CharBlock(
                                required=True,
                                max_length=200,
                                label=_("Sponsors Title"),
                            ),
                        ),
                        (
                            "logos",
                            blocks.ListBlock(
                                SimpleImageBlock(template="components/blocks/media/simple_image.html"),
                                label=_("Sponsor Logos"),
                            ),
                        ),
                    ],
                    icon="group",
                    label=_("Sponsors Section"),
                ),
            ),
            (
                "faq",
                blocks.StructBlock(
                    [
                        (
                            "title",
                            blocks.CharBlock(
                                required=True,
                                max_length=200,
                                label=_("FAQ Title"),
                            ),
                        ),
                        (
                            "items",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        (
                                            "question",
                                            blocks.CharBlock(
                                                required=True,
                                                max_length=200,
                                                label=_("Question"),
                                            ),
                                        ),
                                        (
                                            "answer",
                                            blocks.RichTextBlock(
                                                required=True,
                                                label=_("Answer"),
                                                features=["bold", "italic", "link", "ul", "ol"],
                                            ),
                                        ),
                                    ],
                                    label=_("FAQ Item"),
                                ),
                                label=_("FAQ Items"),
                            ),
                        ),
                    ],
                    icon="help",
                    label=_("FAQ Section"),
                ),
            ),
        ],
        label=_("Event Content"),
        help_text=_("Add content sections for the event."),
    )

    # Layout Options
    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("standard", _("Standard Layout")),
            ("sidebar", _("Sidebar Layout")),
            ("timeline", _("Timeline Layout")),
            ("cards", _("Card Layout")),
        ],
        default="standard",
        label=_("Layout Style"),
    )

    show_toc = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Show Table of Contents"),
        help_text=_("Generate table of contents from headings."),
    )

    show_share = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Share Buttons"),
    )

    class Meta:
        icon = "date"
        label = _(" Event Section")
        group = _("Events")

    def get_headings(self, value):
        """Extract headings from content sections for TOC."""
        headings = []
        for section in value.get("content_sections", []):
            if section.block_type == "heading":
                headings.append(
                    {
                        "text": section.value.get("text"),
                        "level": section.value.get("level", "h2"),
                        "id": self.slugify(section.value.get("text")),
                    }
                )
        return headings

    def slugify(self, text):
        """Create a slug from text for anchor links."""
        import re

        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        text = text.strip("-")
        return text
