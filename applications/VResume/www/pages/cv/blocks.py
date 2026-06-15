"""
CV app blocks — TimelineItemBlock and SkillBlock.
"""
from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class TimelineItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200, required=True, label=_("Title"),
                             help_text=_("Degree, job title, or certification"))
    subtitle = blocks.CharBlock(max_length=200, required=True, label=_("Subtitle"),
                                help_text=_("Institution or company name"))
    date = blocks.CharBlock(max_length=100, required=False, label=_("Date Range"),
                            help_text=_("e.g. 2020 – Present"))
    description = blocks.TextBlock(required=False, label=_("Description"))

    class Meta:
        template = "connect/blocks/timeline_item.html"
        icon = "time"
        label = _("Timeline Item")


class SkillBlock(blocks.StructBlock):
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
        required=False, default="other", label=_("Category"),
    )
    level = blocks.IntegerBlock(
        min_value=0, max_value=100, default=50,
        label=_("Proficiency (0–100)"),
    )

    class Meta:
        template = "connect/blocks/skill.html"
        icon = "star"
        label = _("Skill")
