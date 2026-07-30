"""
Service model — minimal stub to satisfy ``ceptor_ai``'s ``Department.services``
ManyToManyField dependency on ``accounts.Service``.

This model exists only so the ``ceptor_ai`` migration ``0001_initial.py`` can
resolve its ``to='accounts.service'`` reference. The project does not use
departments or services in its own domain — see ``ceptor_ai.transport.handlers.models.manage_service``
for the full ``Service`` implementation.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """Minimal stub model required by the ceptor_ai Department model."""

    name = models.CharField(_("Name"), max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self) -> str:
        return self.name
