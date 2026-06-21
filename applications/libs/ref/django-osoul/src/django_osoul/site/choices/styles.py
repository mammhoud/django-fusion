from django.db import models
from django.utils.translation import gettext_lazy as _


class LayoutOptions(models.TextChoices):
    VERTICAL = "vertical", _("Vertical")
    HORIZONTAL = "horizontal", _("Horizontal")


class ThemeOptions(models.TextChoices):
    THEME_DEFAULT = "theme-default", _("Default")
    THEME_BORDERED = "theme-bordered", _("Bordered")
    THEME_SEMI_DARK = "theme-semi-dark", _("Semi Dark")


class StyleOptions(models.TextChoices):
    LIGHT = "light", _("Light")
    DARK = "dark", _("Dark")
    SYSTEM = "system", _("System Mode")


class ContentLayoutOptions(models.TextChoices):
    COMPACT = "compact", _("Compact")
    WIDE = "wide", _("Wide")


class NavbarTypeOptions(models.TextChoices):
    FIXED = "fixed", _("Fixed")
    STATIC = "static", _("Static")
    HIDDEN = "hidden", _("Hidden")


class HeaderTypeOptions(models.TextChoices):
    STATIC = "static", _("Static")
    FIXED = "fixed", _("Fixed")
