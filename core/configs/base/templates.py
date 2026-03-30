import os  # Noqa
from pathlib import Path  # Noqa

from django.utils.translation import gettext_lazy as _  # Noqa

from configs.base.assets import ASSETS_DIR

from ..settings.conf import Environment
from ..settings.conf import settings as tracker
from ..settings.setup import settings
from .paths import APPS_DIR, BASE_DIR, CORE_DIR

# -------------------------------
# Template Configuration
# -------------------------------
LAYOUT_PATH = settings.get("LAYOUT_PATH", "landing/skeleton.html")
TEMPLATE_DEBUG = settings.get("TEMPLATE_DEBUG", tracker.is_debug)

TEMPLATES_DIRS = [
    Path(APPS_DIR) / "templates",
    Path(ASSETS_DIR) / "templates" / "layout",
    Path(BASE_DIR) / "components",
    Path(CORE_DIR) / "templates",
]

# ------------------------------------------------------------------------------

LAYOUT_PATH = "landing/skeleton.html"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATES_DIRS + [Path(ASSETS_DIR) / "templates",],
        # "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # "wagtail.contrib.settings.context_processors.settings",
                "django_grep.contrib.context.LANGUAGES",
                "django_grep.contrib.context.COOKIES",
                "django_grep.contrib.context.AUTH_SETTINGS",
                "django_grep.contrib.context.CONTEXT",
                "django_grep.contrib.context.SETTINGS",
                # "core.processors.settings_context",
            ],
            "libraries": {
                "embedBlocks": "django_grep.comp.templatetags.embedBlocks",
                "userRole": "django_grep.comp.templatetags.userRole",
            },
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        # "django_cotton.cotton_loader.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "django.template.loaders.filesystem.Loader",
                        # "django_components.template_loader.Loader",
                    ],
                )
            ],
            "builtins": [
                "django.templatetags.static",
                "heroicons.templatetags.heroicons",
                "django_grep.comp.templatetags.components",
                "django_grep.comp.templatetags.apps",
                # "contrib.templatetags.user_role",
            ],
        },
    },
]
# ------------------------------------------------------------------------------

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
# FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "django/crispy"
CRISPY_ALLOWED_TEMPLATE_PACKS = "django/crispy"
# -------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
COMPONENTS = {
    "COMPONENT_DIRS": [
        *TEMPLATES_DIRS,
    ],
    "ENABLE_BLOCK_ATTRS": True,
    "ADD_ASSET_PREFIX": False,
}
# ------------------------------------------------------------------------------
# -------------------------------------------------------------------------------


# WAGTAILTRANSFER_SECRET_KEY = ''
# WAGTAILTRANSFER_SOURCES = {}

# if current_env == Environment.DEMO:
#     WAGTAILTRANSFER_SECRET_KEY = '4ac4822773be75eea36b21a47273b2ae'
#     WAGTAILTRANSFER_SOURCES = {
#     'main': {
#         'BASE_URL': 'https://www.structa.cloud/wagtail-transfer/',
#         'SECRET_KEY': 'ea3ea7cd5daeaf8ea36a7cd5dc2ada7e',
#         },
#     }
# else:
#     WAGTAILTRANSFER_SECRET_KEY = 'ea3ea7cd5daeaf8ea36a7cd5dc2ada7e'
#     WAGTAILTRANSFER_SOURCES = {
#         'demo': {
#             'BASE_URL': 'https://demo.structa.cloud/wagtail-transfer/',
#             'SECRET_KEY': '4ac4822773be75eea36b21a47273b2ae',
#         },
#     }
# WAGTAILTRANSFER_UPDATE_RELATED_MODELS = ['wagtailimages.image']
