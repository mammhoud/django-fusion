from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.fields import StreamField

from core.pages_base import BasePage
from pages.cv.blocks import TimelineItemBlock, SkillBlock


class ResumePage(BasePage):
    template = "base.html"
    template_name = "resume"
    page_title = _("Resume / CV Page")

    education = StreamField(
        [("timeline_item", TimelineItemBlock())],
        use_json_field=True, blank=True,
        verbose_name=_("Education"),
    )
    experience = StreamField(
        [("timeline_item", TimelineItemBlock())],
        use_json_field=True, blank=True,
        verbose_name=_("Experience"),
    )
    skills = StreamField(
        [("skill", SkillBlock())],
        use_json_field=True, blank=True,
        verbose_name=_("Skills"),
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("education"),
        FieldPanel("experience"),
        FieldPanel("skills"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading=_("Content")),
        ObjectList(BasePage.promote_panels, heading=_("Promote")),
        ObjectList(BasePage.settings_panels, heading=_("Settings")),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["page"] = self
        context["education"] = self.education
        context["experience"] = self.experience
        context["skills"] = self.skills
        return context

    class Meta:
        verbose_name = _("Resume Page")
        verbose_name_plural = _("Resume Pages")
        app_label = "cv"
