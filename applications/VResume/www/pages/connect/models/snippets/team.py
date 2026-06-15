from django.db import models
from wagtail.admin.panels import FieldPanel
from django.utils.translation import gettext_lazy as _

class TeamMember(models.Model):
    name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("job_title"),
        FieldPanel("image"),
        FieldPanel("facebook_url"),
        FieldPanel("twitter_url"),
        FieldPanel("linkedin_url"),
        FieldPanel("is_active"),
    ]

    def __str__(self):
        return self.name
