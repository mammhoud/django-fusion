from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList

from core.pages_base import BaseFormPage


class ContactPage(BaseFormPage):
    """
    📞 Contact Page — map embed + contact form.
    Lives in the connect app because it owns form submissions.
    """
    template = "base.html"
    template_name = "contact"
    page_title = _("Contact Page")

    map_embed_url = models.URLField(
        blank=True, max_length=500,
        verbose_name=_("Map Embed URL"),
        help_text=_("Google Maps embed URL"),
    )

    content_panels = BaseFormPage.content_panels + [
        FieldPanel("map_embed_url"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading=_("Content")),
        ObjectList(BaseFormPage.form_settings_panels, heading=_("Form Settings")),
        ObjectList(BaseFormPage.settings_panels, heading=_("Settings")),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["page"] = self
        context["map_embed_url"] = self.map_embed_url
        return context

    class Meta:
        verbose_name = _("Contact Page")
        verbose_name_plural = _("Contact Pages")
        app_label = "connect"
