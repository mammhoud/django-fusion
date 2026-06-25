from django.conf import settings
from django.contrib.sites.models import Site
from django.core.validators import MaxLengthValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from crafts_ai.contrib.core.models import Corporate

# Project-specific imports removed
from crafts_ai.content.models.default import DefaultBase


class Workspace(DefaultBase):
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

    # Core Workspace Fields
    name = models.CharField(
        max_length=100,
        verbose_name=_("Workspace Name"),
        help_text=_("The name of your workspace"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        validators=[MaxLengthValidator(500)],
        help_text=_("Brief description of the workspace (500 chars max)"),
    )
    module = models.CharField(
        max_length=20,
        choices=ModuleChoices.choices,
        default=ModuleChoices.DEVELOPMENT,
        verbose_name=_("Module Type"),
    )
    sites = models.ManyToManyField(
        Site,
        related_name="workspaces",
        verbose_name=_("Associated Sites"),
        help_text=_("Sites this workspace is available on"),
    )
    company = models.ForeignKey(
        Corporate,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="workspaces",
        verbose_name=_("Company"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Is this workspace currently active?"),
    )

    # Template Information
    template_name = models.CharField(
        max_length=255, default="Default", verbose_name=_("Template Name")
    )
    template_suffix = models.CharField(
        max_length=255, default="Template", verbose_name=_("Template Suffix")
    )
    template_version = models.CharField(
        max_length=20,
        default="1.0.0",
        verbose_name=_("Version"),
        help_text=_("Semantic version (e.g., 2.1.5)"),
    )
    template_license = models.CharField(
        max_length=20,
        choices=TemplateLicense.choices,
        default=TemplateLicense.MIT,
        verbose_name=_("License Type"),
    )
    template_free = models.BooleanField(default=False, verbose_name=_("Free Template"))
    template_description = models.TextField(
        default="", verbose_name=_("Template Description"), blank=True
    )
    template_keywords = models.CharField(
        max_length=255,
        default="template,dashboard,admin",
        verbose_name=_("Keywords"),
        help_text=_("Comma-separated keywords for search"),
    )

    # Creator Information
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_workspaces",
        verbose_name=_("Creator"),
        null=True,
        blank=True,
    )
    creator_name = models.CharField(
        max_length=255, default="", verbose_name=_("Creator Name"), blank=True
    )
    creator_url = models.URLField(
        default="",
        verbose_name=_("Creator URL"),
        blank=True,
        validators=[URLValidator()],
    )

    # Social Media Links
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Social Links"),
        help_text=_("Key-value pairs of social media links"),
    )

    # Documentation Links
    documentation_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Documentation Links"),
        help_text=_("Key-value pairs of documentation resources"),
    )

    class Meta:
        db_table = "workspaces"
        verbose_name = _("Workspace")
        verbose_name_plural = _("Workspaces")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["module"]),
            models.Index(fields=["template_name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "company"], name="unique_workspace_name_per_company"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_module_display()})"

    def save(self, *args, **kwargs):
        """Custom save method with additional logic"""
        if not self.creator_name and self.creator:
            self.creator_name = self.creator.get_full_name() or str(self.creator)
        super().save(*args, **kwargs)

    @property
    def full_template_name(self):
        """Returns the complete template name with suffix"""
        return f"{self.template_name} {self.template_suffix}"

    def get_social_link(self, platform):
        """Helper method to get specific social link"""
        return self.social_links.get(platform, "")

    def get_documentation_link(self, resource):
        """Helper method to get specific documentation link"""
        return self.documentation_links.get(resource, "")
