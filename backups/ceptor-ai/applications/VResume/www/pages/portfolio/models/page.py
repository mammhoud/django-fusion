# pyrefly: ignore [missing-import]
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import StreamField

from core.pages_base import BasePage
from pages.portfolio.models.snippets import PortfolioTag, Project


class PortfolioPage(BasePage):
    template = "base.html"
    template_name = "portfolio"
    page_title = _("Portfolio Page")

    _content_panels = BasePage.content_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(_content_panels, heading=_("Content")),
            ObjectList(BasePage.promote_panels, heading=_("Promote")),
            ObjectList(BasePage.settings_panels, heading=_("Settings")),
        ]
    )

    def get_all_tags(self):
        return PortfolioTag.objects.filter(is_active=True).order_by("name")

    def get_context(self, request, *args, **kwargs):
        import json

        context = super().get_context(request, *args, **kwargs)
        context["page"] = self
        tags = self.get_all_tags()
        tags_json = json.dumps([{"slug": tag.slug, "name": tag.name} for tag in tags])
        context.update(
            {
                "featured_projects": Project.objects.filter(
                    is_active=True
                ).order_by("-date_completed"),
                "tags": tags,
                "tags_json": tags_json,
                "current_tags": "",
                "current_q": "",
            }
        )
        return context

    class Meta:
        verbose_name = _("Portfolio Page")
        verbose_name_plural = _("Portfolio Pages")
        app_label = "portfolio"
