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
    BASE_DIR / "pages" / "templates",
    BASE_DIR / "assets" / "templates",
    BASE_DIR.parent / "assets" / "templates",
]

# ------------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATES_DIRS,
        "APP_DIRS": True,  # Enable app template loading for Wagtail and other apps
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                # "core.processors.settings_context",
            ],
            "libraries": {
                # Custom template tags can be added here
            },
            "builtins": [
                "django.templatetags.static",
                "heroicons.templatetags.heroicons",
            ],
        },
    },
]

