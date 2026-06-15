from django.db import models
from wagtail.admin.panels import FieldPanel
from django.utils.translation import gettext_lazy as _


class Skill(models.Model):
    """
    ⭐ Skill snippet - represents a professional skill
    """
    CATEGORY_CHOICES = [
        ("framework", _("Framework")),
        ("language", _("Language")),
        ("tool", _("Tool")),
        ("design", _("Design")),
        ("other", _("Other")),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="tool")
    proficiency = models.IntegerField(default=50, help_text=_("Proficiency level 0-100"))
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("category"),
        FieldPanel("proficiency"),
        FieldPanel("is_visible"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")

    def __str__(self):
        return self.name
