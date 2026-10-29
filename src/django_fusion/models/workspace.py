"""
Workspace models for django-fusion.

A *workspace* is the container a tenant project lives in: a named area of the
admin with its own module type, template identity and optional company owner.
Products extend :class:`AbstractWorkspace` and add their own relations (sites,
membership, branding); the fields here are the ones every consumer shares.

The field set mirrors the concrete ``workspaces`` table that shipped with the
multi-tenant schema, so existing migrations stay in sync with the models.
"""

from django.conf import settings
from django.core.validators import MaxLengthValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel

MODULE_CHOICES = [
    ("dev", _("Development")),
    ("test", _("Testing")),
    ("design", _("Design")),
    ("data", _("Data Science")),
    ("marketing", _("Marketing")),
    ("sales", _("Sales")),
    ("ops", _("Operations")),
]

LICENSE_CHOICES = [
    ("mit", _("MIT License")),
    ("apache", _("Apache License 2.0")),
    ("gpl", _("GNU GPL v3")),
    ("proprietary", _("Proprietary")),
    ("custom", _("Custom License")),
]


class AbstractWorkspace(BaseModel):
    """Abstract workspace shared by every multi-tenant product.

    Attributes:
        name (CharField): Display name, unique per company where a company is set.
        description (TextField): Optional 500-character summary.
        module (CharField): Which product module the workspace belongs to.
        is_active (BooleanField): Soft switch used to hide retired workspaces.
        template_* (mixed): Template identity and licensing metadata.
        creator_* (mixed): Who authored the template, plus their links.
        social_links (JSONField): Free-form ``{network: url}`` map.
        documentation_links (JSONField): Free-form ``{label: url}`` map.
        creator (ForeignKey): Optional user that created the workspace.
    """

    name = models.CharField(
        max_length=100,
        verbose_name=_("Workspace Name"),
        help_text=_("The name of your workspace"),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Brief description of the workspace (500 chars max)"),
        validators=[MaxLengthValidator(500)],
    )
    module = models.CharField(
        max_length=20,
        choices=MODULE_CHOICES,
        default="dev",
        verbose_name=_("Module Type"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Is this workspace currently active?"),
    )
    template_name = models.CharField(
        max_length=255,
        default="Default",
        verbose_name=_("Template Name"),
    )
    template_suffix = models.CharField(
        max_length=255,
        default="Template",
        verbose_name=_("Template Suffix"),
    )
    template_version = models.CharField(
        max_length=20,
        default="1.0.0",
        verbose_name=_("Version"),
        help_text=_("Semantic version (e.g., 2.1.5)"),
    )
    template_license = models.CharField(
        max_length=20,
        choices=LICENSE_CHOICES,
        default="mit",
        verbose_name=_("License Type"),
    )
    template_free = models.BooleanField(
        default=False,
        verbose_name=_("Free Template"),
    )
    template_description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Template Description"),
    )
    template_keywords = models.CharField(
        max_length=255,
        default="template,dashboard,admin",
        verbose_name=_("Keywords"),
        help_text=_("Comma-separated keywords for search"),
    )
    creator_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Creator Name"),
    )
    creator_url = models.URLField(
        blank=True,
        default="",
        validators=[URLValidator()],
        verbose_name=_("Creator URL"),
    )
    social_links = models.JSONField(
        blank=True,
        default=dict,
        verbose_name=_("Social Links"),
        help_text=_("Key-value pairs of social media links"),
    )
    documentation_links = models.JSONField(
        blank=True,
        default=dict,
        verbose_name=_("Documentation Links"),
        help_text=_("Key-value pairs of documentation resources"),
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_workspaces",
        verbose_name=_("Creator"),
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return the workspace name (falling back to the base representation)."""
        return self.name or super().__str__()
