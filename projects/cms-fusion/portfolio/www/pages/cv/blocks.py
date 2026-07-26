"""CV app blocks with VResume-specific templates."""

from django.utils.translation import gettext_lazy as _
from django_fusion.wagtail.blocks import SkillBlock as BaseSkillBlock
from django_fusion.wagtail.blocks import TimelineItemBlock as BaseTimelineItemBlock


class TimelineItemBlock(BaseTimelineItemBlock):
    class Meta:
        template = "connect/blocks/timeline_item.html"
        icon = "time"
        label = _("Timeline Item")


class SkillBlock(BaseSkillBlock):
    class Meta:
        template = "connect/blocks/skill.html"
        icon = "star"
        label = _("Skill")
