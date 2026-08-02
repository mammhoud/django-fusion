from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_fusion.models.workspace import AbstractWorkspace

from apps.domain.contrib.models import Corporate


class Workspace(AbstractWorkspace):
    # Site-specific relationships are kept on the concrete model.
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
    class Meta:
        app_label = "shared"
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

