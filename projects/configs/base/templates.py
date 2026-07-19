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
    BASE_DIR / "assets" / "templates" / "layout",  # resolves "landing/skeleton.html" etc.
    BASE_DIR.parent / "_shared" / "plugins",  # workspace-level shared plugins
    BASE_DIR / "plugins",  # resolve component templates like "components/contact/sections/form/form.html"
    BASE_DIR / "plugins" / "templates",  # resolve plugin-level templates like "notifications/notification.html"
    BASE_DIR / "plugins" / "components",  # resolve plugin-level templates like "notifications/notification.html"
    BASE_DIR.parent / "assets" / "templates",
    BASE_DIR.parent / "assets" / "templates" / "layout",  # workspace-level layout templates
]

COMPONENTS = {
    "COMPONENT_DIRS": [
        *TEMPLATES_DIRS,
    ],
    "ENABLE_BLOCK_ATTRS": True,
    "ADD_ASSET_PREFIX": False,
}
# ------------------------------------------------------------------------------
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
# Register django_fusion component tags (comp, slot, prop, var, css, js) as builtins
# so templates can use {% comp %} without needing {% load components %} every time.
# Avoid importing django_fusion.comp.configuration.conf here. That module
# imports django.conf.settings and reads settings.DEBUG at import time; because
# this file is itself imported while Django settings are still being built,
# touching settings.DEBUG creates a circular import that re-enters the site
# settings module before INSTALLED_APPS is defined. The constants below are
# the canonical builtin module paths exported by django-fusion.
if importlib.util.find_spec("django_fusion") is not None:
    _TEMPLATE_BUILTINS.append("django_fusion.comp.templatetags.components")
    # Register ui_tags (table, pagination, search, form) as builtins
    _TEMPLATE_BUILTINS.append("django_fusion.templatetags.ui_tags")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATES_DIRS,
        "APP_DIRS": True,  # Enable app template loading for Wagtail and other apps
        "OPTIONS": {
            "context_processors": _CONTEXT_PROCESSORS,
            "libraries": {
                # Register component tags for {% load components %} compatibility.
                # It's also registered as a builtin, but {% load %} needs the library entry.
                "components": "django_fusion.comp.templatetags.components",
                "ui_tags": "django_fusion.templatetags.ui_tags",
            },
            "builtins": _TEMPLATE_BUILTINS,
        },
    },
]

