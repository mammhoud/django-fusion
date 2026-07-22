from django.db import models
from wagtail.admin.panels import FieldPanel
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """
    💼 Service snippet - represents a service offered
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, default="folder-open")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("is_active"),
        FieldPanel("order"),
    ]

    class Meta:
        app_label = "connect"
        ordering = ["order", "name"]
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self):
        return self.name
