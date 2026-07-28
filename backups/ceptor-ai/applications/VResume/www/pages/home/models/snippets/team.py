from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel


class TeamMember(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    job_title = models.CharField(max_length=255, verbose_name=_("Job Title"))
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image"),
    )
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    twitter_url = models.URLField(blank=True, verbose_name=_("Twitter URL"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("LinkedIn URL"))
    portfolio_url = models.URLField(blank=True, verbose_name=_("Portfolio URL"))
    contact_url = models.URLField(blank=True, verbose_name=_("Contact URL"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    panels = [
        FieldPanel("name"),
        FieldPanel("job_title"),
        FieldPanel("image"),
        FieldPanel("facebook_url"),
        FieldPanel("twitter_url"),
        FieldPanel("linkedin_url"),
        FieldPanel("portfolio_url"),
        FieldPanel("contact_url"),
        FieldPanel("is_active"),
    ]

    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")
        app_label = "home"

    def __str__(self):
        return self.name
