from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


@register_setting(name="vresume_settings")
class VResumeSettings(BaseSiteSetting):
    """Global site settings — personal info, social links, branding."""

    avatar = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text=_("Avatar image displayed in the sidebar"),
    )
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text=_("Company or personal logo"),
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text=_("Browser favicon (small square image)"),
    )
    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"))
    job_title = models.CharField(max_length=255, verbose_name=_("Job Title"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    birthday = models.DateField(null=True, blank=True, verbose_name=_("Birthday"))
    location = models.CharField(max_length=255, blank=True, verbose_name=_("Location"))
    map_embed_url = models.URLField(
        blank=True, max_length=500,
        verbose_name=_("Map Embed URL"),
        help_text=_("Google Maps embed URL for the contact page"),
    )
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    twitter_url = models.URLField(blank=True, verbose_name=_("Twitter URL"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("LinkedIn URL"))
    github_url = models.URLField(blank=True, verbose_name=_("GitHub URL"))
    instagram_url = models.URLField(blank=True, verbose_name=_("Instagram URL"))

    panels = [
        FieldPanel("avatar"),
        FieldPanel("logo"),
        FieldPanel("favicon"),
        MultiFieldPanel([
            FieldPanel("full_name"),
            FieldPanel("job_title"),
            FieldPanel("email"),
            FieldPanel("phone"),
            FieldPanel("birthday"),
            FieldPanel("location"),
            FieldPanel("map_embed_url"),
        ], heading=_("Personal Info")),
        MultiFieldPanel([
            FieldPanel("facebook_url"),
            FieldPanel("twitter_url"),
            FieldPanel("linkedin_url"),
            FieldPanel("github_url"),
            FieldPanel("instagram_url"),
        ], heading=_("Social Links")),
    ]

    class Meta:
        verbose_name = _("vResume Settings")
        verbose_name_plural = _("vResume Settings")
        app_label = "home"

    def __str__(self):
        return f"vResume Settings — {self.full_name}"
