from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel

class Testimonial(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    job_title = models.CharField(max_length=255, blank=True, verbose_name=_("Job Title"))
    text = models.TextField(verbose_name=_("Testimonial Text"))
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Photo"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    panels = [
        FieldPanel("name"),
        FieldPanel("job_title"),
        FieldPanel("text"),
        FieldPanel("image"),
        FieldPanel("is_active"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        app_label = "about"

    def __str__(self):
        return self.name
