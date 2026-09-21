# ====================================
# 👑 Django Admin Configuration (Unfold)
# ====================================
from django.utils.translation import gettext_lazy as _

from ..settings.conf import settings

# -------------------------------
# Admin Configuration
# -------------------------------
# Unfold titles come from the UNFOLD dict's own SITE_HEADER / SITE_TITLE /
# INDEX_TITLE keys (below). The former module-level ADMIN_SITE_HEADER /
# ADMIN_SITE_TITLE / ADMIN_INDEX_TITLE settings had no reader anywhere in the
# repository and were removed 2026-09-21 (deletion-manifest DOC-0033).
ADMIN_URL = settings.get("ADMIN_URL", "admin/")

# -------------------------------
# Site Admins & Managers
# -------------------------------
ADMINS = settings.get("ADMINS", [("Admin", "admin@example.com")])
MANAGERS = settings.get("MANAGERS", ADMINS)
SITE_ID = settings.get("SITE_ID", 1)

# -------------------------------
# Wagtail Settings
# -------------------------------
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "Structa Cloud")
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
# sidebar navigation, and site-specific items in its own settings module
# (after ``from configs.default import *``).  See:
#   projects/Clients/ctc-research/backend/settings/site.py — CTC Research identity
#   projects/Clients/platform/backend/settings.py          — platform site
# The previously listed paths (projects/portfolio, projects/fusion-cms,
# projects/lms) do not exist in this repository.
UNFOLD = {
    # ── Branding ──────────────────────────────────────────────────────────
    "SITE_HEADER": _("Structa Cloud"),
    "SITE_TITLE": _("Structa Cloud Admin"),
    "INDEX_TITLE": _("Dashboard"),
    "SITE_SYMBOL": "cloud",

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
        {"icon": "bolt", "title": _("Task Center"), "link": "/tasks/"},
    ],

    # ── Sidebar Navigation ─────────────────────────────────────────────────
    # ``show_all_applications=True`` lets Django auto-discover registered
    # apps so LMS sites get a correct sidebar without hardcoded model links.
    # A site may override this with a curated navigation in its own
    # settings.py. The retired per-site override is gone, so none does.
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
# Removed 2026-09-21 (deletion-manifest DOC-0034): ADMIN_PERMISSIONS was never
# read by any module, template, or command. Its keys described gates that were
# not wired to anything, so it advertised an access-control posture the code
# did not enforce. Real authorization lives in Django permissions, Wagtail's
# page/workflow permissions, and each app's view-level checks.

# -------------------------------
# Admin Security Settings
# -------------------------------
# Removed 2026-09-21 (deletion-manifest DOC-0035): ADMIN_SECURITY was never
# read by any module, template, or command, so REQUIRE_2FA, IP_WHITELIST,
# MAX_LOGIN_ATTEMPTS, LOCKOUT_TIME and SESSION_TIMEOUT were inert -- a declared
# security posture that nothing enforced.
#
# Real settings, so operators stop reaching for the removed dict:
#   session lifetime  -> SESSION_COOKIE_AGE (set in configs/settings/CD/*.py)
#   admin URL gate    -> configs/base/urls.py + the ADMIN_URL setting above
#   HTTPS/HSTS/cookies-> configs/base/security.py
#   two-factor auth   -> the installed `mfa` app's own settings, not this file
