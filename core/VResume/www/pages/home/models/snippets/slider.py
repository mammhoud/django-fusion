from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail import blocks


class SliderLinkBlock(blocks.StructBlock):
    """A single link with icon for slider CTA buttons."""
    label = blocks.CharBlock(max_length=100, label=_("Label"))
    url = blocks.URLBlock(label=_("URL"))
    icon = blocks.CharBlock(
        max_length=50, required=False,
        label=_("Icon Class"),
        help_text=_("Remix icon class, e.g. ri-arrow-right-line"),
    )

    class Meta:
        icon = "link"
        label = _("Link")


class Slider(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    subtitle = models.CharField(max_length=255, blank=True, verbose_name=_("Subtitle"))
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image"),
    )
    links = StreamField(
        [("link", SliderLinkBlock())],
        use_json_field=True, blank=True,
        verbose_name=_("Links"),
        help_text=_("Add one or more CTA links with icons"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("image"),
        FieldPanel("links"),
        FieldPanel("is_active"),
    ]

    class Meta:
        verbose_name = _("Slider")
        verbose_name_plural = _("Sliders")
        app_label = "home"

    def __str__(self):
        return self.title
