"""POS Cloud — Django settings with Unfold Admin, django-bolt, django-fusion."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "formint-cloud-secret-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# ── Tenancy (django-tenants — schema-per-tenant) ─────────────────
# Schema-based multi-tenancy is PostgreSQL-only. The full django-tenants
# stack (SHARED/TENANT app split, tenant router, TenantMainMiddleware,
# Postgres engine, public URLconf) activates ONLY when DB_ENGINE is set to
# the django_tenants backend. Under SQLite (dev default) everything runs
# exactly as before — the tenant middleware and router are simply absent.
TENANCY_ENABLED = os.environ.get("DB_ENGINE", "").startswith("django_tenants")

# Apps that live in the shared `public` schema (registry: Tenant, Domain,
# Django auth/admin, and the third-party admin/designer stack).
SHARED_APPS = [
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

    # Wagtail (required by django-fusion core models)
    "wagtail",
    "wagtail.admin",

    # Third-party
    "channels",
    "django_fusion",
    "rest_framework",
    "django_filters",
    "django_bolt",

    # POS Cloud (precis-style apps/ package)
    "apps.core.apps.CoreConfig",
    "apps.domain.apps.DomainConfig",
    "apps.handlers.apps.HandlersConfig",
    "apps.tasks",
]

# Apps replicated into EVERY tenant schema (tenant-scoped tables).
# admin/wagtail/unfold stay public-only; Django auth is duplicated per
# tenant so each tenant has its own user set.
TENANT_APPS = [
    "daphne",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "django_fusion",
    "rest_framework",
    "django_filters",
    "django_bolt",
    "apps.core.apps.CoreConfig",
    "apps.domain.apps.DomainConfig",
    "apps.handlers.apps.HandlersConfig",
    "apps.tasks",
]

if TENANCY_ENABLED:
    SHARED_APPS.insert(0, "django_tenants")

# Under SQLite the effective app list is exactly the current (shared) set;
# under PostgreSQL it is shared + tenant apps (deduped, order preserved).
INSTALLED_APPS = list(SHARED_APPS) + [
    a for a in TENANT_APPS if a not in SHARED_APPS
]

TENANT_MODEL = "core.Tenant"
TENANT_DOMAIN_MODEL = "core.Domain"
PUBLIC_SCHEMA_URLCONF = "configs.urls_public"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Inject WebSocket event listener into bolt dashboard pages
    "apps.handlers.middleware.BoltSyncEventsMiddleware",
    # JSON 401 (not a login redirect) for anonymous /api/* viewset calls
    "apps.handlers.middleware.ApiAuthMiddleware",
]
if TENANCY_ENABLED:
    # Resolves the tenant schema from the Host header (django-tenants).
    MIDDLEWARE.insert(1, "django_tenants.middleware.main.TenantMainMiddleware")
    # Hardening: reject Hosts outside ALLOWED_HOSTS before tenant lookup.
    MIDDLEWARE.insert(2, "django_tenants.middleware.main.TenantHostnameValidationMiddleware")
    # Serve the public URLconf for hosts with no matching tenant Domain
    # (e.g. a bare `localhost` in dev) instead of returning 404.
    SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

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
# Under SQLite (dev default) the ENGINE stays sqlite3; when DB_ENGINE is
# flipped to django_tenants.postgresql_backend, schema-per-tenant activates
# and the tenant router routes shared vs tenant tables.
DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "DB_ENGINE",
            "django_tenants.postgresql_backend"
            if TENANCY_ENABLED
            else "django.db.backends.sqlite3",
        ),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "formint_cloud.db")),
    }
}
if os.environ.get("DB_HOST"):
    DATABASES["default"].update({
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ.get("DB_PORT", "5432"),
        "USER": os.environ.get("DB_USER", "formint_cloud"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    })
if TENANCY_ENABLED:
    DATABASE_ROUTERS = ["django_tenants.routers.TenantSyncRouter"]

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
    "SITE_ICON": {
        "light": "/static/pos-crest.svg",
        "dark": "/static/pos-crest.svg",
    },
    "SITE_LOGO": {
        "light": "/static/pos-crest.svg",
        "dark": "/static/pos-crest.svg",
    },
    "SITE_SYMBOL": "store",
    # Custom KPI dashboard context (rendered by templates/admin/index.html).
    "DASHBOARD_CALLBACK": "configs.dashboard.dashboard_callback",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "THEME": "dark",
    # Tactical Telemetry design system — shared SCSS token layer
    # (source: apps/core/static/tactical/scss/, build: make styles).
    "STYLES": ["/static/tactical/css/tactical.css"],
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
                    {"title": "Device Tokens", "icon": "key", "link": "/admin/core/devicetoken/"},
                    {"title": "Sync Logs", "icon": "sync", "link": "/admin/core/branchsynclog/"},
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
# Wagtail (minimal — only needed by django-fusion model imports)
# ══════════════════════════════════════════════════════════════════════

WAGTAIL_SITE_NAME = "POS Cloud"
WAGTAILADMIN_BASE_URL = "http://localhost:8082"
WAGTAIL_I18N_ENABLED = False

# ══════════════════════════════════════════════════════════════════════
# django-fusion Component Configuration
# ══════════════════════════════════════════════════════════════════════

COMPONENTS_INCLUDE_PATH_ROOTS = [
    str(BASE_DIR / "apps" / "handlers" / "fragments"),
]

FUSION_SITE_NAME = "formint_cloud"
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
