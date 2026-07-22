"""POS Cloud — Django settings with Unfold Admin, django-bolt, django-fusion."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "pos-cloud-secret-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# ── Applications ──
INSTALLED_APPS = [
    # Daphne ASGI server (must be first for runserver compatibility)
    "daphne",

    # Unfold admin (must come before django.contrib.admin)
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",

    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "channels",
    "django_fusion",
    "rest_framework",
    "django_filters",
    "django_bolt",

    # POS Cloud
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Inject WebSocket event listener into bolt dashboard pages
    "core.middleware.BoltSyncEventsMiddleware",
]

ROOT_URLCONF = "configs.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "configs.wsgi.application"
ASGI_APPLICATION = "configs.asgi.application"

# ── Channels layer (in-memory — no Redis required for dev) ──
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# ── Database ──
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "pos_cloud.db")),
    }
}
if os.environ.get("DB_HOST"):
    DATABASES["default"].update({
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ.get("DB_PORT", "5432"),
        "USER": os.environ.get("DB_USER", "pos_cloud"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    })

# ── Internationalization ──
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── Static files ──
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ══════════════════════════════════════════════════════════════════════
# Unfold Admin Theme
# ══════════════════════════════════════════════════════════════════════

UNFOLD = {
    "SITE_TITLE": "POS Cloud",
    "SITE_HEADER": "POS Cloud — Multi-Branch Management",
    "SITE_SUBHEADER": "Organizations • Branches • Leads • Reports",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_SYMBOL": "store",
    "DASHBOARD": "configs.dashboard.POSCloudDashboard",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "THEME": "dark",
    "COLORS": {
        "primary": {
            "50": "240 253 244",
            "100": "209 250 229",
            "200": "167 243 208",
            "300": "110 231 183",
            "400": "52 211 153",
            "500": "16 185 129",
            "600": "5 150 105",
            "700": "4 120 87",
            "800": "6 95 70",
            "900": "6 78 59",
            "950": "2 44 34",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Organizations",
                "items": [
                    {"title": "Organizations", "icon": "corporate_fare", "link": "/admin/core/organization/"},
                    {"title": "Branches", "icon": "store", "link": "/admin/core/branch/"},
                ],
            },
            {
                "title": "CRM",
                "items": [
                    {"title": "Leads", "icon": "person_add", "link": "/admin/core/lead/"},
                    {"title": "Contacts", "icon": "contacts", "link": "/admin/core/contact/"},
                    {"title": "Companies", "icon": "business", "link": "/admin/core/company/"},
                    {"title": "Deals", "icon": "handshake", "link": "/admin/core/deal/"},
                ],
            },
            {
                "title": "Reports",
                "items": [
                    {"title": "Inventory Reports", "icon": "inventory_2", "link": "/admin/core/inventoryreport/"},
                    {"title": "Branch Reports", "icon": "analytics", "link": "/admin/core/branchreport/"},
                    {"title": "Sales Reports", "icon": "trending_up", "link": "/reports/sales/"},
                ],
            },
            {
                "title": "POS Data",
                "items": [
                    {"title": "Products", "icon": "inventory_2", "link": "/admin/core/branchproduct/"},
                    {"title": "Sales", "icon": "shopping_cart", "link": "/admin/core/branchsale/"},
                    {"title": "Inventory", "icon": "warehouse", "link": "/admin/core/branchinventory/"},
                ],
            },
            {
                "title": "System",
                "items": [
                    {"title": "Users", "icon": "person", "link": "/admin/auth/user/"},
                    {"title": "Groups", "icon": "groups", "link": "/admin/auth/group/"},
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": ["core.organization", "core.branch"],
            "items": [
                {"title": "Organizations", "link": "/admin/core/organization/"},
                {"title": "Branches", "link": "/admin/core/branch/"},
            ],
        },
        {
            "models": ["core.lead", "core.deal"],
            "items": [
                {"title": "Leads", "link": "/admin/core/lead/"},
                {"title": "Deals", "link": "/admin/core/deal/"},
            ],
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════
# django-fusion Component Configuration
# ══════════════════════════════════════════════════════════════════════

COMPONENTS_INCLUDE_PATH_ROOTS = [
    str(BASE_DIR / "core" / "fragments"),
]

FUSION_SITE_NAME = "pos_cloud"
FUSION_SITE_TITLE = "POS Cloud Platform"

# ══════════════════════════════════════════════════════════════════════
# django-bolt Configuration
# ══════════════════════════════════════════════════════════════════════

BOLT_SETTINGS = {
    "SITE_TITLE": "POS Cloud Data",
    "ENABLE_EXPORT": True,
    "EXPORT_FORMATS": ["csv", "xlsx", "json"],
    "DEFAULT_PAGE_SIZE": 50,
    "ENABLE_CHARTS": True,
}
