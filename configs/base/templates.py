import importlib.util
import os  # Noqa
from pathlib import Path  # Noqa

from django.utils.translation import gettext_lazy as _  # Noqa

from ..settings.conf import Environment
from ..settings.conf import settings as conf_settings
from ..settings.setup import settings
from .paths import BASE_DIR

# -------------------------------
# Template Configuration
# -------------------------------
TEMPLATE_DEBUG = settings.get("TEMPLATE_DEBUG", conf_settings.is_debug)

TEMPLATES_DIRS = [
    BASE_DIR / "templates",
    BASE_DIR / "pages" / "templates",
    BASE_DIR / "www" / "pages" / "templates",
    BASE_DIR / "assets" / "templates",
    BASE_DIR.parent / "assets" / "templates",
    # Component templates (notifications, modals, forms, htmx utilities, search, tables)
    # are now located directly inside assets/templates/<category>/
    # packages/ui is no longer a separate template root.
]

# ------------------------------------------------------------------------------

_CONTEXT_PROCESSORS = [
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.i18n",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
]
if importlib.util.find_spec("wagtail") is not None:
    _CONTEXT_PROCESSORS.append("wagtail.contrib.settings.context_processors.settings")

_TEMPLATE_BUILTINS = ["django.templatetags.static"]
if importlib.util.find_spec("heroicons") is not None:
    _TEMPLATE_BUILTINS.append("heroicons.templatetags.heroicons")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATES_DIRS,
        "APP_DIRS": True,  # Enable app template loading for Wagtail and other apps
        "OPTIONS": {
            "context_processors": _CONTEXT_PROCESSORS,
            "libraries": {
                # Custom template tags can be added here
            },
            "builtins": _TEMPLATE_BUILTINS,
        },
    },
]

