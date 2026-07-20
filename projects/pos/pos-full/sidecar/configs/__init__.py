"""
POS Full — Master Manager Django Settings with Unfold Admin.

Centralized Django configuration for the pos-full sidecar server.
pos-full is the master manager with Django Admin (Unfold theme).
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR.parent / "restaurant.db"

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
    # Django admin (themed by Unfold)
    "django.contrib.admin",
    # POS Full managed models
    "models.PosFullConfig",
]

# ── Middleware ──
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# ── URL Configuration ──
ROOT_URLCONF = "configs.urls"

# ── Templates (required for admin) ──
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# ── Static files (admin CSS/JS) ──
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Unfold Admin Theme Settings ──
UNFOLD = {
    "SITE_TITLE": "POS Full — Master Manager",
    "SITE_HEADER": "POS Full Admin",
    "SITE_SUBHEADER": "Branch Device & Data Management",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_SYMBOL": "dashboard",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
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
            {"title": "Nodes & Sync", "items": [
                {"title": "Nodes", "icon": "dns", "link": "/admin/pos_full/node/"},
                {"title": "Sync Logs", "icon": "sync", "link": "/admin/pos_full/synclog/"},
                {"title": "Device Configs", "icon": "settings", "link": "/admin/pos_full/deviceconfig/"},
                {"title": "Cloud Links", "icon": "cloud", "link": "/admin/pos_full/cloudlink/"},
            ]},
            {"title": "System", "items": [
                {"title": "Users", "icon": "person", "link": "/admin/auth/user/"},
                {"title": "Groups", "icon": "groups", "link": "/admin/auth/group/"},
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
