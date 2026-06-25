from django.db import models
from django.utils.translation import gettext_lazy as _


class ModuleTypes(models.TextChoices):
    LEAD = "lead", _("Lead")
    TASK = "task", _("Task")
    PROJECT = "project", _("Project")
