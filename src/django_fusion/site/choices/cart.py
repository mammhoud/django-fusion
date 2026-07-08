from django.db import models
from django.utils.translation import gettext_lazy as _


class CartStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    SAVED = "saved", _("Saved")
    EMPTY = "empty", _("Empty")
