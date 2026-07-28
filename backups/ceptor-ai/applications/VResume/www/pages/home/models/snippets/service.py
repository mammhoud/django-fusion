from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(
        max_length=100, blank=True, default="folder-open",
        verbose_name=_("Icon Class"),
        help_text=_("Bootstrap icon class, e.g. bi-code-square"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    link_1_url = models.URLField(blank=True, verbose_name=_("Link 1 URL"))
    link_1_text = models.CharField(max_length=100, blank=True, verbose_name=_("Link 1 Text"))
    link_2_url = models.URLField(blank=True, verbose_name=_("Link 2 URL"))
    link_2_text = models.CharField(max_length=100, blank=True, verbose_name=_("Link 2 Text"))

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("is_active"),
        FieldPanel("order"),
        MultiFieldPanel([
            FieldPanel("link_1_url"),
            FieldPanel("link_1_text"),
            FieldPanel("link_2_url"),
            FieldPanel("link_2_text"),
        ], heading=_("Links")),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        app_label = "home"

    def __str__(self):
        return self.name
