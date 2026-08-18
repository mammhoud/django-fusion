# Project-specific imports removed
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_fusion.models.default import DefaultBase


class Branch(DefaultBase):
    """
    Represents a branch location of a corporate entity
    """

    name = models.CharField(max_length=100, verbose_name=_("Branch Name"))
    corporate = models.ForeignKey(
        Corporate, on_delete=models.CASCADE, related_name="branches", verbose_name=_("Corporate")
    )
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Branch Code"))
    location = models.CharField(max_length=255, verbose_name=_("Location"))
    address = models.TextField(verbose_name=_("Full Address"))
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Main Phone"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Branch Email"))
    manager = models.ForeignKey(
        "Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branches",
        verbose_name=_("Branch Manager"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_headquarters = models.BooleanField(default=False, verbose_name=_("Is Headquarters"))
    opening_date = models.DateField(null=True, blank=True, verbose_name=_("Opening Date"))
    opening_time = models.TimeField(verbose_name=_("Opening Time"))
    closing_time = models.TimeField(verbose_name=_("Closing Time"))

    class Meta:
        app_label = "shared"
        verbose_name = _("Branch")
        verbose_name_plural = _("Branches")
        db_table = "branches"
        ordering = ["corporate", "name"]

    def __str__(self):
        return f"{self.name} ({self.corporate.name})"
