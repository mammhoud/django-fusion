from django.db import models
from wagtail.admin.panels import FieldPanel
from django.utils.translation import gettext_lazy as _

class Slider(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    link_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("image"),
        FieldPanel("link_url"),
        FieldPanel("is_active"),
    ]

    def __str__(self):
        return self.title
