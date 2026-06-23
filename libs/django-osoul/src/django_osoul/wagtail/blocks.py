"""Reusable base Wagtail blocks for Structa Cloud sites."""

from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class TimelineItemBlock(blocks.StructBlock):
    """Generic timeline entry for experience, education, or milestones."""

    title = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Title"),
        help_text=_("Degree, job title, milestone, or certification"),
    )
    subtitle = blocks.CharBlock(
        max_length=200,
        required=True,
        label=_("Subtitle"),
        help_text=_("Institution, company, or supporting label"),
    )
    date = blocks.CharBlock(
        max_length=100,
        required=False,
        label=_("Date Range"),
        help_text=_("e.g. 2020 – Present"),
    )
    description = blocks.TextBlock(required=False, label=_("Description"))

    class Meta:
        icon = "time"
        label = _("Timeline Item")


class SkillBlock(blocks.StructBlock):
    """Generic skill entry with a category and proficiency level."""

    name = blocks.CharBlock(max_length=100, required=True, label=_("Skill Name"))
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
    )
    level = blocks.IntegerBlock(
        min_value=0,
        max_value=100,
        default=50,
        label=_("Proficiency (0–100)"),
    )

    class Meta:
        icon = "star"
        label = _("Skill")
