from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.fields import StreamField

from wagtail.snippets.blocks import SnippetChooserBlock

from core.pages_base import BasePage
from pages.about.models.snippets import Testimonial, Client
from pages.home.models.snippets import TeamMember


class AboutPage(BasePage):
    template = "base.html"
    template_name = "about"
    page_title = _("About Page")

    bio = StreamField(
        [("bio_text", blocks.RichTextBlock(label=_("Bio Text")))],
        use_json_field=True, blank=True,
        verbose_name=_("Bio"),
    )
    testimonials = StreamField(
        [("testimonial", SnippetChooserBlock(Testimonial))],
        use_json_field=True, blank=True,
        verbose_name=_("Testimonials"),
    )
    clients = StreamField(
        [("client", SnippetChooserBlock(Client))],
        use_json_field=True, blank=True,
        verbose_name=_("Clients"),
    )
    team = StreamField(
        [("team_member", SnippetChooserBlock(TeamMember))],
        use_json_field=True, blank=True,
        verbose_name=_("Team Section"),
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("bio"),
        FieldPanel("team"),
        FieldPanel("testimonials"),
        FieldPanel("clients"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading=_("Content")),
        ObjectList(BasePage.promote_panels, heading=_("Promote")),
        ObjectList(BasePage.settings_panels, heading=_("Settings")),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["page"] = self
        context["bio"] = self.bio
        context["team"] = self.team
        context["testimonials"] = self.testimonials
        context["clients"] = self.clients
        return context

    class Meta:
        verbose_name = _("About Page")
        verbose_name_plural = _("About Pages")
        app_label = "about"
