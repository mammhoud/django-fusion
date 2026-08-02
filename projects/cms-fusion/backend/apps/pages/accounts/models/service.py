"""
Service model — managed via the accounts snippets (ServiceViewSet).

The model is used by the admin/snippet interface to manage services and
by content models that reference services (see ``apps.pages.accounts.snippets``).
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """Service managed through the admin snippet interface."""

    name = models.CharField(_("Name"), max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self) -> str:
        return self.name
