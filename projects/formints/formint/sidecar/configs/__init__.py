"""
POS Full — Master Manager Django Settings with Unfold Admin.

Centralized Django configuration for the pos-full sidecar server.
pos-full is the master manager with Django Admin (Unfold theme).
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR.parent / "restaurant.db"

# ── Optional django-bolt (high-performance Rust-backed API) ────────────────
# The django-fusion ``apis`` plugin checks this at runtime: when django-bolt is
# installed, Application viewsets can also be mounted as bolt routes (same
# dual-mode respond contract). Kept optional so the project runs without it.
HAS_DJANGO_BOLT = importlib.util.find_spec("django_bolt") is not None

# ── Django Core ──
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "pos-full-master-secret-key")
DEBUG = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Database ──
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DB_PATH),
    }
}

# ── Installed Apps ──
INSTALLED_APPS = [
    # django-bolt high-performance API framework (optional)
    *(("django_bolt",) if HAS_DJANGO_BOLT else ()),
    # Unfold — modern admin theme (must come before django.contrib.admin)
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    # Django core (required for admin)
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Django Channels (WebSocket support; replaces Robyn WS)
    "channels",
    # Django admin (themed by Unfold)
    "django.contrib.admin",
    # Wagtail (required by django_fusion.core.models.mixins.display_mode)
    "wagtail",
    # django-fusion local library (DataToken sync tracking, fusion rendering)
    "django_fusion",
    # POS Full managed models
    "models.PosFullConfig",
    # Formint app (merged from backend/ — loyalty, settings, ninja API,
    # fusion render-mode contract; app_label="formint")
    "formint",
    # Ninja + ninja-extra API layer (django-fusion encoder/decoder)
    "ninja",
    "ninja_extra",
    "django_htmx",
    "django_tables2",
]

# ── Middleware ──
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Seeds the session fusion render-mode from the operator's UserSettings
    # row (admin settings page) — see formint/middleware.py. Needs auth +
    # session middleware to have run first.
    "formint.middleware.FormintSessionModeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# ── URL Configuration ──
ROOT_URLCONF = "configs.urls"

# ── ASGI / Channels (replaces Robyn server) ────────────────────────────
ASGI_APPLICATION = "asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver", "0.0.0.0"]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True

# ── Fusion Render Mode (django-fusion dual-mode contract) ───────────────
#   True  → "fusion render first" — Django serves finished server-rendered
#           HTML (or fusion-encoded JSON) as the source of truth.
#   False → "data APIs" — the client renders from /api/v1/* JSON.
# Per-request override: ``X-Fusion-Render-First: true|false`` header.
# Per-session preference: ``request.session['fusion_render_first']`` (set by
# ``django_fusion.routes.rendering.session.FusionSessionChecker``) sits
# between the header override and the configured default.
FUSION_RENDER_FIRST_DEFAULT = os.environ.get("FUSION_RENDER_FIRST", "1") == "1"
COMPONENTS_DIR_NAMES = ("components", "partials", "tags")

# ── django-fusion component registry (see FORMINT_ARCHITECTURE.md §12) ────
# COMPONENTS_ENABLE_BLOCK_ATTRS — emit data-block-* attributes on components
# for headless/CMS inspection and stable component identity in the HTML.
COMPONENTS_ENABLE_BLOCK_ATTRS = True
# COMPONENTS_INCLUDE_PATH_ROOTS — template subdirectories whose *.html files
# are auto-registered as path-style components ({% comp %} / include bridge).
COMPONENTS_INCLUDE_PATH_ROOTS = (
    "components",
    "partials",
    "formint",
)

# ── Superuser bootstrap (used by manage.py --ensure-superuser) ──
FORMINT_ADMIN_EMAIL = os.environ.get("FORMINT_ADMIN_EMAIL", "admin@formint.local")
FORMINT_ADMIN_PASSWORD = os.environ.get("FORMINT_ADMIN_PASSWORD", "admin123")
FORMINT_ADMIN_NAME = os.environ.get("FORMINT_ADMIN_NAME", "Formint Admin")

# ── Templates (required for admin) ──
# DIRS contains only django_templates/ (a Django-only template tree). The
# sibling templates/ dir is the Robyn/Jinja2 admin tree and must NOT be
# exposed to Django (its Jinja2 syntax would break Django template loading).
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "django_templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            # django-fusion component tags (comp, slot, prop, var) — registered
            # so `{% load components %}` works (mirrors landing-fusion).
            "libraries": {
                "components": "django_fusion.comp.templatetags.components",
            },
        },
    },
]

# ── Static files (admin CSS/JS) ──
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Unfold Admin Theme Settings ──
UNFOLD = {
    "SITE_TITLE": "Formint POS — Master Manager",
    "SITE_HEADER": "Formint POS Admin",
    "SITE_SUBHEADER": "Merged Master Manager · Branch, Loyalty & Settings",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_SYMBOL": "dashboard",
    # Legacy unfold DashboardView path (older unfold builds)
    "DASHBOARD": "configs.dashboard.POSDashboardView",
    # Modern unfold (>= 0.80) dashboard callback — injects KPI/charts/tables
    "DASHBOARD_CALLBACK": "configs.dashboard.pos_dashboard_callback",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "LOGIN": {
        "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
    },
    "THEME": "dark",  # dark | light
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
            {"title": "POS Core", "items": [
                {"title": "Products", "icon": "inventory_2", "link": "/admin/pos_full/product/"},
                {"title": "Categories", "icon": "category", "link": "/admin/pos_full/category/"},
                {"title": "Customers", "icon": "people", "link": "/admin/pos_full/customer/"},
                {"title": "Sales", "icon": "shopping_cart", "link": "/admin/pos_full/sale/"},
                {"title": "Employees", "icon": "badge", "link": "/admin/pos_full/employee/"},
                {"title": "Inventory", "icon": "warehouse", "link": "/admin/pos_full/inventorytransaction/"},
            ]},
            {"title": "Operations", "items": [
                {"title": "Suppliers", "icon": "local_shipping", "link": "/admin/pos_full/supplier/"},
                {"title": "Purchase Orders", "icon": "receipt_long", "link": "/admin/pos_full/purchaseorder/"},
                {"title": "Kitchen Tickets", "icon": "restaurant", "link": "/admin/pos_full/kitchenticket/"},
                {"title": "Support Tickets", "icon": "support", "link": "/admin/pos_full/supportticket/"},
                {"title": "Menu", "icon": "menu_book", "link": "/admin/pos_full/menu/"},
            ]},
            {"title": "Loyalty & Clients", "items": [
                {"title": "Client Categories", "icon": "workspace_premium", "link": "/admin/pos_full/clientcategory/"},
                {"title": "Loyalty Transactions", "icon": "stars", "link": "/admin/pos_full/loyaltytransaction/"},
                {"title": "Customers (People)", "icon": "people_alt", "link": "/admin/pos_full/customer/"},
            ]},
            {"title": "Nodes & Sync", "items": [
                {"title": "Nodes", "icon": "dns", "link": "/admin/pos_full/node/"},
                {"title": "Sync Logs", "icon": "sync", "link": "/admin/pos_full/synclog/"},
                {"title": "Device Configs", "icon": "settings", "link": "/admin/pos_full/deviceconfig/"},
                {"title": "Cloud Links", "icon": "cloud", "link": "/admin/pos_full/cloudlink/"},
            ]},
            {"title": "Settings", "items": [
                {"title": "User Settings", "icon": "manage_accounts", "link": "/admin/pos_full/usersettings/"},
                {"title": "Users", "icon": "person", "link": "/admin/auth/user/"},
                {"title": "Groups", "icon": "groups", "link": "/admin/auth/group/"},
            ]},
            {"title": "System", "items": [
                {"title": "Server Settings", "icon": "tune", "link": "/admin/settings"},
            ]},
        ],
    },
    "TABS": [
        {
            "models": ["pos_full.product", "models.category"],
            "items": [
                {"title": "Products", "link": "/admin/pos_full/product/"},
                {"title": "Categories", "link": "/admin/pos_full/category/"},
            ],
        },
        {
            "models": ["pos_full.sale", "models.customer"],
            "items": [
                {"title": "Sales", "link": "/admin/pos_full/sale/"},
                {"title": "Customers", "link": "/admin/pos_full/customer/"},
            ],
        },
    ],
}

# ── Server Config ──
HOST = os.environ.get("POS_FULL_HOST", "0.0.0.0")
PORT = int(os.environ.get("POS_FULL_PORT", "8766"))
API_KEY = os.environ.get("POS_FULL_API_KEY", None)
CLOUD_CRM_URL = os.environ.get("CLOUD_CRM_URL", "")
CLOUD_API_KEY = os.environ.get("CLOUD_API_KEY", None)
