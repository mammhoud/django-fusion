from django.db import models
from wagtail.admin.panels import FieldPanel
from django.utils.translation import gettext_lazy as _


class Testimonial(models.Model):
    """
    💬 Testimonial snippet - represents a client or user testimonial
    """
    name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("job_title"),
        FieldPanel("text"),
        FieldPanel("image"),
        FieldPanel("is_active"),
        FieldPanel("order"),
    ]

    class Meta:
        app_label = "connect"
        ordering = ["order", "name"]
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")

    def __str__(self):
        return self.name
