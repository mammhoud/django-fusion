from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel

@register_snippet
class FusionBranding(models.Model):
    site_name = models.CharField(max_length=100, default='Fusion')
    company_name = models.CharField(max_length=100, default='Fusion Inc.')
    creator_name = models.CharField(max_length=100, default='Fusion Team')
    primary_color = models.CharField(max_length=7, default='#00a1b3')
    favicon = models.ImageField(upload_to='branding/', blank=True)

    panels = [
        FieldPanel('site_name'),
        FieldPanel('company_name'),
        FieldPanel('creator_name'),
        FieldPanel('primary_color'),
        FieldPanel('favicon'),
    ]

    class Meta:
        verbose_name = 'Fusion Branding'
        verbose_name_plural = 'Fusion Brandings'

    def __str__(self):
        return self.site_name
