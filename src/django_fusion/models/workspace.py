"""Reusable workspace model base for Fusion sites."""

from django.conf import settings
from django.core.validators import MaxLengthValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_fusion.models.default import DefaultBase


class AbstractWorkspace(DefaultBase):
    """Shared workspace fields and behavior.

    Site applications add their own site/company relationship fields while
    inheriting this stable, reusable workspace core.
    """

    class ModuleChoices(models.TextChoices):
        DEVELOPMENT = "dev", _("Development")
        TESTING = "test", _("Testing")
        DESIGN = "design", _("Design")
        DATA_SCIENCE = "data", _("Data Science")
        MARKETING = "marketing", _("Marketing")
        SALES = "sales", _("Sales")
        OPERATIONS = "ops", _("Operations")

    class TemplateLicense(models.TextChoices):
        MIT = "mit", _("MIT License")
        APACHE = "apache", _("Apache License 2.0")
        GPL = "gpl", _("GNU GPL v3")
        PROPRIETARY = "proprietary", _("Proprietary")
        CUSTOM = "custom", _("Custom License")

    name = models.CharField(max_length=100, verbose_name=_("Workspace Name"), help_text=_("The name of your workspace"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"), validators=[MaxLengthValidator(500)], help_text=_("Brief description of the workspace (500 chars max)"))
    module = models.CharField(max_length=20, choices=ModuleChoices.choices, default=ModuleChoices.DEVELOPMENT, verbose_name=_("Module Type"))
    template_name = models.CharField(max_length=255, default="Default", verbose_name=_("Template Name"))
    template_suffix = models.CharField(max_length=255, default="Template", verbose_name=_("Template Suffix"))
    template_version = models.CharField(max_length=20, default="1.0.0", verbose_name=_("Version"), help_text=_("Semantic version (e.g., 2.1.5)"))
    template_license = models.CharField(max_length=20, choices=TemplateLicense.choices, default=TemplateLicense.MIT, verbose_name=_("License Type"))
    template_free = models.BooleanField(default=False, verbose_name=_("Free Template"))
    template_description = models.TextField(default="", verbose_name=_("Template Description"), blank=True)
    template_keywords = models.CharField(max_length=255, default="template,dashboard,admin", verbose_name=_("Keywords"), help_text=_("Comma-separated keywords for search"))
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_workspaces", verbose_name=_("Creator"), null=True, blank=True)
    creator_name = models.CharField(max_length=255, default="", verbose_name=_("Creator Name"), blank=True)
    creator_url = models.URLField(default="", verbose_name=_("Creator URL"), blank=True, validators=[URLValidator()])
    social_links = models.JSONField(default=dict, blank=True, verbose_name=_("Social Links"), help_text=_("Key-value pairs of social media links"))
    documentation_links = models.JSONField(default=dict, blank=True, verbose_name=_("Documentation Links"), help_text=_("Key-value pairs of documentation resources"))
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Is this workspace currently active?"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} ({self.get_module_display()})"

    def save(self, *args, **kwargs):
        if not self.creator_name and self.creator:
            self.creator_name = self.creator.get_full_name() or str(self.creator)
        super().save(*args, **kwargs)

    @property
    def full_template_name(self):
        return f"{self.template_name} {self.template_suffix}"

    def get_social_link(self, platform):
        return self.social_links.get(platform, "")

    def get_documentation_link(self, resource):
        return self.documentation_links.get(resource, "")
