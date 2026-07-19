"""
Page Blocks - Reusable content blocks for page models
"""
from django.utils.translation import gettext_lazy as _
from wagtail.images.blocks import ImageChooserBlock
from wagtail import blocks


class TestimonialBlock(blocks.StructBlock):
    """
    💬 Testimonial block for client testimonials in vResume.
    """
    avatar = ImageChooserBlock(
        required=False,
        label=_("Avatar"),
        help_text=_("Client's avatar image"),
        template="blocks/media/image_lite.html",
    )
    name = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Name"),
        help_text=_("Client's name"),
    )
    text = blocks.TextBlock(
        required=True,
        label=_("Testimonial"),
        help_text=_("The testimonial text"),
    )

    class Meta:
        template = "pages/blocks/testimonial.html"
        icon = "quote"
        label = _("Testimonial")


class ClientBlock(blocks.StructBlock):
    """
    👥 Client/Logo block for displaying client logos.
    """
    logo = ImageChooserBlock(
        required=True,
        label=_("Logo"),
        help_text=_("Client's logo image"),
        template="blocks/media/image_lite.html",
    )
    name = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Name"),
        help_text=_("Client name for alt text"),
    )

    class Meta:
        template = "pages/blocks/client.html"
        icon = "user"
        label = _("Client")


class TimelineItemBlock(blocks.StructBlock):
    """
    📅 Timeline item block for education and experience sections.
    """
    title = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Title"),
        help_text=_("Degree, job title, or certification"),
    )
    subtitle = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Subtitle"),
        help_text=_("Institution or company name"),
    )
    date = blocks.CharBlock(
        max_length=100,
        required=False,
        label=_("Date Range"),
        help_text=_("e.g., 2020 - Present"),
    )
    description = blocks.TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Additional details about this entry"),
    )

    class Meta:
        template = "pages/blocks/timeline_item.html"
        icon = "time"
        label = _("Timeline Item")


class ContactFormBlock(blocks.StructBlock):
    """
    📧 Simple contact form block.
    """
    show_name = blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Show Name Field"),
        help_text=_("Display name input field in the form"),
    )
    show_phone = blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Show Phone Field"),
        help_text=_("Display phone input field in the form"),
    )
    show_subject = blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Show Subject Field"),
        help_text=_("Display subject input field in the form"),
    )
    button_text = blocks.CharBlock(
        default=_("Send Message"),
        max_length=50,
        label=_("Submit Button Text"),
        help_text=_("Text displayed on the form submit button"),
    )

    class Meta:
        template = "pages/blocks/contact_form.html"
        icon = "form"
        label = _("Contact Form")
        help_text = _("A simple contact form block for collecting visitor inquiries")


class SkillBlock(blocks.StructBlock):
    """
    ⚡ Skill block with proficiency level and category.
    """
    name = blocks.CharBlock(
        max_length=100,
        required=True,
        label=_("Skill Name"),
        help_text=_("Name of the skill"),
    )
    category = blocks.ChoiceBlock(
        choices=[
            ("ide", _("IDE")),
            ("agent", _("Agent")),
            ("tool", _("Tool")),
            ("language", _("Language")),
            ("framework", _("Framework")),
            ("other", _("Other")),
        ],
        required=False,
        default="other",
        label=_("Category"),
        help_text=_("Skill category for grouping"),
    )
    level = blocks.IntegerBlock(
        min_value=0,
        max_value=100,
        default=50,
        label=_("Proficiency Level"),
        help_text=_("Proficiency level from 0 to 100"),
    )

    class Meta:
        template = "pages/blocks/skill.html"
        icon = "star"
        label = _("Skill")
