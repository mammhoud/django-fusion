from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Client Name"))
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=False, blank=False,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Logo"),
    )
    url = models.URLField(blank=True, verbose_name=_("Website URL"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    panels = [
        FieldPanel("name"),
        FieldPanel("logo"),
        FieldPanel("url"),
        FieldPanel("is_active"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        app_label = "about"

    def __str__(self):
        return self.name
