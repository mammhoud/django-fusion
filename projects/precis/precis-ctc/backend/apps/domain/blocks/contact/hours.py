from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from ..base import BaseBlock

__all__ = ["BusinessHoursBlock"]


class BusinessHoursBlock(BaseBlock):
    """
    Business operating hours display.
    """

    title = blocks.CharBlock(max_length=100, default=_("Business Hours"), label=_("Section Title"))

    hours = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("days", blocks.CharBlock(max_length=50, label=_("Days"))),
                ("hours", blocks.CharBlock(max_length=50, label=_("Hours"))),
                (
                    "is_closed",
                    blocks.BooleanBlock(default=False, required=False, label=_("Closed")),
                ),
                ("note", blocks.CharBlock(required=False, max_length=100, label=_("Note"))),
            ]
        ),
        default=[
            {"days": "Monday - Friday", "hours": "9:00 AM - 6:00 PM"},
            {"days": "Saturday", "hours": "10:00 AM - 4:00 PM"},
            {"days": "Sunday", "hours": "Closed", "is_closed": True},
        ],
        label=_("Hours Entries"),
    )

    timezone = blocks.CharBlock(
        max_length=50, default="EST", label=_("Timezone"), help_text=_("e.g., EST, PST, GMT+1")
    )

    show_current_status = blocks.BooleanBlock(
        default=True,
        label=_("Show Current Status"),
        help_text=_("Display whether currently open or closed"),
    )

    emergency_hours_note = blocks.TextBlock(
        required=False,
        label=_("Emergency Hours Note"),
        help_text=_("Note for after-hours emergencies"),
    )

    class Meta:
        icon = "time"
        label = _("Business Hours")
