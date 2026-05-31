# ====================================
# 👑 Django Admin Configuration (Unfold)
# ====================================
from django.templatetags.static import static
from django.urls import reverse_lazy
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
UNFOLD = {
    # ── Branding ──────────────────────────────────────────────────────────────
    "SITE_HEADER": _("VResume"),
    "SITE_TITLE": _("VResume Admin"),
    "INDEX_TITLE": _("Dashboard"),
    "SITE_SYMBOL": "person",

    # ── Display Options ────────────────────────────────────────────────────────
    "SHOW_LANGUAGES": True,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,

    # ── Site URL & Dropdown ────────────────────────────────────────────────────
    "SITE_URL": "/",
    "SITE_DROPDOWN": [
        {
            "icon": "home",
            "title": _("View Site"),
            "link": "/",
        },
        {
            "icon": "edit_note",
            "title": _("Wagtail CMS"),
            "link": "/admin/",
        },
    ],

    # ── Login Page ─────────────────────────────────────────────────────────────
    "LOGIN": {
        "image": lambda request: static("images/avatar/01.jpg"),
    },

    # ── Sidebar Navigation ─────────────────────────────────────────────────────
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Dashboard"),
                "separator": False,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Content"),
                "separator": True,
                "items": [
                    {
                        "title": _("Blog Posts"),
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_blogpost_changelist"),
                    },
                    {
                        "title": _("Blog Authors"),
                        "icon": "person",
                        "link": reverse_lazy("admin:blog_blogauthor_changelist"),
                    },
                    {
                        "title": _("Blog Tags"),
                        "icon": "label",
                        "link": reverse_lazy("admin:blog_blogtag_changelist"),
                    },
                ],
            },
            {
                "title": _("Portfolio"),
                "separator": True,
                "items": [
                    {
                        "title": _("Projects"),
                        "icon": "work",
                        "link": reverse_lazy("admin:portfolio_project_changelist"),
                    },
                    {
                        "title": _("Portfolio Tags"),
                        "icon": "sell",
                        "link": reverse_lazy("admin:portfolio_portfoliotag_changelist"),
                    },
                ],
            },
            {
                "title": _("Connect"),
                "separator": True,
                "items": [
                    {
                        "title": _("Form Submissions"),
                        "icon": "inbox",
                        "link": reverse_lazy("admin:connect_formsubmission_changelist"),
                    },
                    {
                        "title": _("Subscribers"),
                        "icon": "group",
                        "link": reverse_lazy("admin:connect_subscriber_changelist"),
                    },
                    {
                        "title": _("Campaigns"),
                        "icon": "campaign",
                        "link": reverse_lazy("admin:connect_campaign_changelist"),
                    },
                    {
                        "title": _("Email Deliveries"),
                        "icon": "mail",
                        "link": reverse_lazy("admin:connect_emaildelivery_changelist"),
                    },
                ],
            },
            {
                "title": _("Site Settings"),
                "separator": True,
                "items": [
                    {
                        "title": _("vResume Settings"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:home_vresumesettings_changelist"),
                    },
                    {
                        "title": _("Services"),
                        "icon": "build",
                        "link": reverse_lazy("admin:home_service_changelist"),
                    },
                    {
                        "title": _("Testimonials"),
                        "icon": "format_quote",
                        "link": reverse_lazy("admin:home_testimonial_changelist"),
                    },
                    {
                        "title": _("Team Members"),
                        "icon": "people",
                        "link": reverse_lazy("admin:home_teammember_changelist"),
                    },
                    {
                        "title": _("Sliders"),
                        "icon": "view_carousel",
                        "link": reverse_lazy("admin:home_slider_changelist"),
                    },
                ],
            },
            {
                "title": _("Automation"),
                "separator": True,
                "items": [
                    {
                        "title": _("Periodic Tasks"),
                        "icon": "schedule",
                        "link": reverse_lazy("admin:django_celery_beat_periodictask_changelist"),
                    },
                    {
                        "title": _("Crontab Schedules"),
                        "icon": "timer",
                        "link": reverse_lazy("admin:django_celery_beat_crontabschedule_changelist"),
                    },
                    {
                        "title": _("Interval Schedules"),
                        "icon": "repeat",
                        "link": reverse_lazy("admin:django_celery_beat_intervalschedule_changelist"),
                    },
                ],
            },
            {
                "title": _("Users & Auth"),
                "separator": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "manage_accounts",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group_work",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },

    # ── Color Palette (purple primary) ─────────────────────────────────────────
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

    # ── Custom Scripts & Styles ────────────────────────────────────────────────
    # Only include files that actually exist in static/
    "SCRIPTS": [],
    "STYLES": [],

    # ── Callbacks ─────────────────────────────────────────────────────────────
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
