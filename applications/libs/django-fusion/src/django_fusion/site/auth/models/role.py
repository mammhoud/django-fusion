from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    Role model for defining user roles and permissions within the system.
    """

    class RoleType(models.TextChoices):
        ADMIN = "ADMIN", _("Administrator")
        MANAGER = "MANAGER", _("Manager")
        EDITOR = "EDITOR", _("Editor")
        CONTRIBUTOR = "CONTRIBUTOR", _("Contributor")
        VIEWER = "VIEWER", _("Viewer")
        CUSTOM = "CUSTOM", _("Custom")

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Role Name"),
        help_text=_("Unique name for this role (e.g., Admin, Manager, User)."),
    )

    role_type = models.CharField(
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.CUSTOM,
        verbose_name=_("Role Type"),
        help_text=_("Category of role"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of this role"),
    )

    permissions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Permissions"),
        help_text=_("JSON structure defining role permissions"),
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Is Default Role"),
        help_text=_("Assign this role to new users by default"),
    )

    level = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Role Level"),
        help_text=_("Hierarchical level (higher = more permissions)"),
    )

    group = models.OneToOneField(
        Group,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Group"),
        help_text=_("Link to a Django group"),
    )

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        app_label = "django_fusion"
        db_table = "profile_roles"
        ordering = ["level", "name"]
        indexes = [
            models.Index(fields=["role_type"]),
            models.Index(fields=["is_default"]),
            models.Index(fields=["level"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Ensure only one default role exists."""
        super().clean()
        if self.is_default:
            existing_default = Role.objects.filter(is_default=True).exclude(pk=self.pk)
            if existing_default.exists():
                raise ValidationError(_("Only one role can be set as default."))

    def has_permission(self, perm_codename):
        for group in self.groups.all():
            if group.permissions.filter(codename=perm_codename).exists():
                return True
        return False
