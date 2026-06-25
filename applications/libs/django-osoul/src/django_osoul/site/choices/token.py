from django.db import models
from django.utils.translation import gettext_lazy as _


class Privacy(models.TextChoices):
    PRIVATE = "Private", _("Private")
    TEAM = "Team", _("Team")
    PUBLIC = "Public", _("Public")


class TokenTypes(models.TextChoices):
    EA = "EA", _("Email Activation")
    SU = "SU", _("Subscription")
    PERM = "PERM", _("Permissions")
    C = "C", _("Common")
