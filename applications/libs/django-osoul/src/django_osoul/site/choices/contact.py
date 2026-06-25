from django.db import models
from django.utils.translation import gettext_lazy as _


# Extended Phone Model for Multiple Phone Numbers
class PhoneType(models.TextChoices):
    MOBILE = "mobile", _("Mobile")
    HOME = "home", _("Home")
    WORK = "work", _("Work")


class EmailType(models.TextChoices):
    TEXT = "TEXT", _("Text")
    DEDIC = "ATTACHED", _("Dedicated")
