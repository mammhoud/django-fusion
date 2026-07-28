# ====================================
# 👑 Django Admin Configuration (Unfold)
# ====================================
from django.utils.translation import gettext_lazy as _

from ..settings.setup import settings

# -------------------------------
# Admin Configuration
# -------------------------------
ADMIN_URL = settings.get("ADMIN_URL", "admin/")
ADMIN_SITE_HEADER = settings.get("ADMIN_SITE_HEADER", "VResume Admin")
ADMIN_SITE_TITLE = settings.get("ADMIN_SITE_TITLE", "VResume Admin")
ADMIN_INDEX_TITLE = settings.get("ADMIN_INDEX_TITLE", "Site Administration")

# -------------------------------
# Site Admins & Managers
# -------------------------------
ADMINS = settings.get("ADMINS", [("Admin", "admin@example.com")])
MANAGERS = settings.get("MANAGERS", ADMINS)
SITE_ID = settings.get("SITE_ID", 1)

# -------------------------------
# Wagtail Settings
# -------------------------------
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "VResume")
WAGTAILADMIN_BASE_URL = settings.get("WAGTAILADMIN_BASE_URL", "http://localhost:8000")
BASE_URL = settings.get("BASE_URL", WAGTAILADMIN_BASE_URL)
WAGTAIL_ENABLE_UPDATE_CHECK = settings.get("WAGTAIL_ENABLE_UPDATE_CHECK", False)
WAGTAIL_PASSWORD_MANAGEMENT_ENABLED = settings.get("WAGTAIL_PASSWORD_MANAGEMENT_ENABLED", True)
WAGTAIL_PASSWORD_RESET_ENABLED = settings.get("WAGTAIL_PASSWORD_RESET_ENABLED", True)

# -------------------------------
# Migrations
# -------------------------------
MIGRATION_MODULES = settings.get("MIGRATION_MODULES", {})

# -------------------------------
# Admin Template Configuration (Unfold)
# -------------------------------
# This is a minimal shared baseline.  Each website overrides branding,
# sidebar navigation, and site-specific items in its own settings.py
# (after ``from configs.settings import *``).  See:
#   projects/portfolio/settings.py  — full VResume sidebar with page-model links
#   projects/fusion-cms/settings.py
#   projects/lms/settings.py
UNFOLD = {
    # ── Branding ──────────────────────────────────────────────────────────
    "SITE_HEADER": _("Admin"),
    "SITE_TITLE": _("Site Admin"),
    "INDEX_TITLE": _("Dashboard"),
    "SITE_SYMBOL": "school",

    # ── Display Options ────────────────────────────────────────────────────
    "SHOW_LANGUAGES": True,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,

    # ── Site URL & Dropdown ────────────────────────────────────────────────
    "SITE_URL": "/",
    "SITE_DROPDOWN": [
        {"icon": "home", "title": _("View Site"), "link": "/"},
        {"icon": "edit_note", "title": _("Wagtail CMS"), "link": "/admin/"},
    ],

    # ── Sidebar Navigation ─────────────────────────────────────────────────
    # ``show_all_applications=True`` lets Django auto-discover registered
    # apps so LMS sites get a correct sidebar without hardcoded model links.
    # VResume overrides this in its settings.py with a curated navigation.
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },

    # ── Color Palette (purple primary) ─────────────────────────────────────
    "COLORS": {
        "base": {
            "50":  "249 250 251",
            "100": "243 244 246",
            "200": "229 231 235",
            "300": "209 213 219",
            "400": "156 163 175",
            "500": "107 114 128",
            "600": "75 85 99",
            "700": "55 65 81",
            "800": "31 41 55",
            "900": "17 24 39",
            "950": "3 7 18",
        },
        "primary": {
            "50":  "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
        "font": {
            "subtle-light":    "var(--color-base-500)",
            "subtle-dark":     "var(--color-base-400)",
            "default-light":   "var(--color-base-600)",
            "default-dark":    "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark":  "var(--color-base-100)",
        },
    },

    # ── Custom Scripts & Styles ────────────────────────────────────────────
    "SCRIPTS": [],
    "STYLES": [],

    # ── Callbacks ─────────────────────────────────────────────────────────
    "ENVIRONMENT_CALLBACK": None,
    "DASHBOARD_CALLBACK": None,
}

# -------------------------------
# Admin Permission Settings
# -------------------------------
ADMIN_PERMISSIONS = {
    "CREATE_SUPERUSER": settings.get("ADMIN_CREATE_SUPERUSER", True),
    "DELETE_SUPERUSER": settings.get("ADMIN_DELETE_SUPERUSER", False),
    "EDIT_SUPERUSER": settings.get("ADMIN_EDIT_SUPERUSER", True),
    "VIEW_LOGS": settings.get("ADMIN_VIEW_LOGS", True),
    "EXPORT_DATA": settings.get("ADMIN_EXPORT_DATA", True),
}

# -------------------------------
# Admin Security Settings
# -------------------------------
ADMIN_SECURITY = {
    "SESSION_TIMEOUT": settings.get("ADMIN_SESSION_TIMEOUT", 120),  # minutes
    "MAX_LOGIN_ATTEMPTS": settings.get("ADMIN_MAX_LOGIN_ATTEMPTS", 5),
    "LOCKOUT_TIME": settings.get("ADMIN_LOCKOUT_TIME", 15),  # minutes
    "REQUIRE_2FA": settings.get("ADMIN_REQUIRE_2FA", settings.is_production),
    "IP_WHITELIST": settings.get("ADMIN_IP_WHITELIST", []),
}
