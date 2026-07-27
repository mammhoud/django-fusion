import logging

from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock

logger = logging.getLogger(__name__)

__all__ = ["TestimonialBlock"]


class TestimonialBlock(BaseBlock):
    """
    Enhanced customer testimonial with rating, verification, and multiple layout options.
    """

    testimonial_text = blocks.RichTextBlock(
        required=True,
        label=_("Testimonial Text"),
        features=["bold", "italic", "link"],
        help_text=_("What the person said about your product/service."),
    )

    customer_name = blocks.CharBlock(
        required=True,
        max_length=100,
        label=_("Customer Name"),
    )

    customer_title = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Customer Title"),
        help_text=_("Job title or position."),
    )

    company = blocks.CharBlock(
        required=False,
        max_length=100,
        label=_("Company"),
        help_text=_("Company or organization name."),
    )

    company_logo = ImageChooserBlock(
        required=False,
        label=_("Company Logo"),
    )

    avatar = ImageChooserBlock(
        required=False,
        label=_("Customer Photo"),
    )

    rating = blocks.IntegerBlock(
        required=False,
        min_value=1,
        max_value=5,
        label=_("Rating"),
        help_text=_("Star rating from 1 to 5."),
    )

    show_rating = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Show Star Rating"),
    )

    date = blocks.DateBlock(
        required=False,
        label=_("Testimonial Date"),
    )

    verified = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Verified Customer"),
        help_text=_("Mark as verified purchase or interaction"),
    )

    verification_text = blocks.CharBlock(
        required=False,
        default=_("Verified Customer"),
        max_length=50,
        label=_("Verification Text"),
    )

    layout_style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("card", _("Card Layout")),
            ("simple", _("Simple Layout")),
            ("horizontal", _("Horizontal Layout")),
            ("quote", _("Quote Style")),
            ("grid", _("Grid Layout")),
        ],
        default="card",
        label=_("Layout Style"),
    )

    testimonial_source = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("customer", _("Customer")),
            ("client", _("Client")),
            ("colleague", _("Colleague")),
            ("partner", _("Partner")),
            ("student", _("Student")),
            ("other", _("Other")),
        ],
        default="customer",
        label=_("Source Type"),
    )

    video_testimonial = EmbedBlock(
        required=False,
        label=_("Video Testimonial"),
        help_text=_("Embed a video testimonial from YouTube, Vimeo, etc."),
    )

    class Meta:
        icon = "group"
        label = _("Testimonial")
        group = _("Content")
