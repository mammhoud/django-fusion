import importlib.util
import os  # Noqa
from pathlib import Path  # Noqa

from django.utils.translation import gettext_lazy as _  # Noqa

from ..settings.conf import Environment
from ..settings.conf import settings

conf_settings = settings
from .paths import BASE_DIR

# -------------------------------
# Template Configuration
# -------------------------------
TEMPLATE_DEBUG = settings.get("TEMPLATE_DEBUG", conf_settings.is_debug)

# Template search paths are listed for **both** supported layouts so the
# same settings work on the host and inside the Docker backend image:
#
# * Container layout — the site backend is mounted directly at the site
#   root (``/app/<site>``), so ``BASE_DIR`` *is* the Django root and the
#   page/component trees live under ``BASE_DIR/apps/...``.
# * Host layout — ``active_site_dir()`` resolves to the project folder
#   (``projects/<site>``) while the Django root is ``projects/<site>/backend``,
#   so the same trees live under ``BASE_DIR/backend/apps/...``.
#
# Django's filesystem loader silently skips missing directories, so listing
# both layouts is safe in either environment and keeps the ``{% comp %}``
# resolver (which scans these dirs plus app template dirs) able to find both
# dotted components (``components/.../name/name.html``) and direct-path
# templates (``about/sections/about.html``).
TEMPLATES_DIRS = [
    # ── Site root templates ──────────────────────────────────────────
    BASE_DIR / "templates",
    BASE_DIR / "backend" / "templates",
    # ── Site-wide shared templates (home, about, contact, services, team) ──
    BASE_DIR / "apps" / "templates",
    BASE_DIR / "backend" / "apps" / "templates",
    # ── Page model + component templates (apps/pages/pages, accounts) ──
    BASE_DIR / "apps" / "pages" / "pages" / "templates",
    BASE_DIR / "backend" / "apps" / "pages" / "pages" / "templates",
    BASE_DIR / "apps" / "pages" / "accounts" / "templates",
    BASE_DIR / "backend" / "apps" / "pages" / "accounts" / "templates",
    # ── Assets + workspace-level shared templates ────────────────────
    BASE_DIR / "assets" / "templates",
    BASE_DIR / "assets" / "templates" / "layout",  # resolves "landing/skeleton.html" etc.
    BASE_DIR / "backend" / "assets" / "templates",
    BASE_DIR.parent / "assets" / "templates",  # workspace-level shared templates (notifications, errors, certs, etc.)
    BASE_DIR.parent / "assets" / "templates" / "layout",
]
# django-fusion ships templates under its own package, including the
# new ``fusion/`` component namespace and legacy stubs. Resolve the
# directory without importing django_fusion submodules to avoid
# circular imports during settings construction.
_django_fusion_spec = importlib.util.find_spec("django_fusion")
if _django_fusion_spec is not None:
    if _django_fusion_spec.origin:
        TEMPLATES_DIRS.append(Path(_django_fusion_spec.origin).parent / "templates")
    elif _django_fusion_spec.submodule_search_locations:
        TEMPLATES_DIRS.append(Path(_django_fusion_spec.submodule_search_locations[0]) / "templates")

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
# Avoid importing django_fusion.config.conf here. That module
# imports django.conf.settings and reads settings.DEBUG at import time; because
# this file is itself imported while Django settings are still being built,
# touching settings.DEBUG creates a circular import that re-enters the site
# settings module before INSTALLED_APPS is defined. The constants below are
# the canonical builtin module paths exported by django-fusion.
if importlib.util.find_spec("django_fusion") is not None:
    # Component tags (table, pagination, search, form, modal, etc.)
    _TEMPLATE_BUILTINS.append("django_fusion.comp.templatetags.components")
    # Fusion layout tags (fusion_layout, fusion_render_first_flag, etc.)
    _TEMPLATE_BUILTINS.append("django_fusion.comp.templatetags.fusion_layout")

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
                # Register fusion_layout for {% load fusion_layout %} compatibility.
                "fusion_layout": "django_fusion.comp.templatetags.fusion_layout",
            },
            "builtins": _TEMPLATE_BUILTINS,
        },
    },
]

