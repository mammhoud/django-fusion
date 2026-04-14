# ====================================
# 👑 Django Admin Configuration
# ====================================
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from ..settings.conf import settings

# -------------------------------
# Admin Configuration
# -------------------------------
ADMIN_URL = settings.get("ADMIN_URL", "control/")
ADMIN_SITE_HEADER = settings.get("ADMIN_SITE_HEADER", "Admin Panel")
ADMIN_SITE_TITLE = settings.get("ADMIN_SITE_TITLE", "Admin Panel")
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
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "CTC_Hub")
WAGTAILADMIN_BASE_URL = settings.get("WAGTAILADMIN_BASE_URL", "/admin/")
WAGTAIL_ENABLE_UPDATE_CHECK = settings.get("WAGTAIL_ENABLE_UPDATE_CHECK", False)
WAGTAIL_PASSWORD_MANAGEMENT_ENABLED = settings.get("WAGTAIL_PASSWORD_MANAGEMENT_ENABLED", True)
WAGTAIL_PASSWORD_RESET_ENABLED = settings.get("WAGTAIL_PASSWORD_RESET_ENABLED", True)

# -------------------------------
# Migrations
# -------------------------------
MIGRATION_MODULES = settings.get(
    "MIGRATION_MODULES", {"sites": "django_rseal.contrib.migrations"}
)

# ====================================
# 🎨 Unfold Admin (UNFOLD = ADMIN_TEMPLATE)
# Single source of truth for admin UI config.
# ====================================
UNFOLD = {
    "SITE_TITLE": _(settings.get("ADMIN_SITE_TITLE", "Structa Admin")),
    "SITE_HEADER": _(settings.get("ADMIN_SITE_HEADER", "Structa")),
    "SITE_URL": settings.get("ADMIN_SITE_URL", "/"),
    "SITE_SYMBOL": settings.get("ADMIN_SITE_SYMBOL", "speed"),
    "SHOW_LANGUAGES": settings.get("ADMIN_SHOW_LANGUAGES", True),
    "SHOW_HISTORY": settings.get("ADMIN_SHOW_HISTORY", True),
    "SHOW_VIEW_ON_SITE": settings.get("ADMIN_SHOW_VIEW_ON_SITE", True),
    "SHOW_BACK_BUTTON": settings.get("ADMIN_SHOW_BACK_BUTTON", False),
    "SITE_DROPDOWN": settings.get(
        "ADMIN_SITE_DROPDOWN",
        [{"icon": "diamond", "title": _("My site"), "link": "/"}],
    ),
    "LOGIN": {
        "image": lambda request: static(
            settings.get("ADMIN_LOGIN_BACKGROUND", "images/bg/bg-g1.webp")
        )
    },
    "SIDEBAR": {
        "show_search": settings.get("ADMIN_SIDEBAR_SHOW_SEARCH", True),
        "show_all_applications": settings.get("ADMIN_SIDEBAR_SHOW_ALL_APPS", False),
        "application_package": settings.get("ADMIN_SIDEBAR_APP_PACKAGE", True),
        "navigation": [
            {
                "title": _("Content"),
                "items": [
                    {
                        "title": _("Pages"),
                        "icon": "article",
                        "link": reverse_lazy("wagtailadmin_home"),
                    },
                    {
                        "title": _("Blog"),
                        "icon": "rss_feed",
                        "link": reverse_lazy("wagtailsnippets:list", args=["blog", "blogpage"]),
                    },
                ],
            },
            {
                "title": _("Users & Auth"),
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": _("Social Accounts"),
                        "icon": "link",
                        "link": reverse_lazy("admin:socialaccount_socialaccount_changelist"),
                    },
                ],
            },
            {
                "title": _("LMS"),
                "items": [
                    {"title": _("Courses"), "icon": "school", "link": reverse_lazy("admin:lms_course_changelist")},
                    {"title": _("Modules"), "icon": "layers", "link": reverse_lazy("admin:lms_module_changelist")},
                    {"title": _("Lessons"), "icon": "menu_book", "link": reverse_lazy("admin:lms_lesson_changelist")},
                    {"title": _("Quizzes"), "icon": "quiz", "link": reverse_lazy("admin:lms_quiz_changelist")},
                    {"title": _("Certificates"), "icon": "workspace_premium", "link": reverse_lazy("admin:lms_certificate_changelist")},
                ],
            },
            {
                "title": _("Registration"),
                "items": [
                    {"title": _("Persons"), "icon": "badge", "link": reverse_lazy("admin:handlers_person_changelist")},
                    {
                        "title": _("Email Templates"),
                        "icon": "mail",
                        "link": reverse_lazy("wagtailsnippets:list", args=["registration", "authemailtemplate"]),
                    },
                ],
            },
            {
                "title": _("System"),
                "items": [
                    {"title": _("Sites"), "icon": "dns", "link": reverse_lazy("admin:sites_site_changelist")},
                    {"title": _("Redirects"), "icon": "redirect", "link": reverse_lazy("admin:redirects_redirect_changelist")},
                    {"title": _("Log Entries"), "icon": "history", "link": reverse_lazy("admin:admin_logentry_changelist")},
                ],
            },
        ],
    },
    "COLORS": settings.get(
        "ADMIN_COLORS",
        {
            "base": {
                "50": "249, 250, 251", "100": "243, 244, 246", "200": "229, 231, 235",
                "300": "209, 213, 219", "400": "156, 163, 175", "500": "107, 114, 128",
                "600": "75, 85, 99",   "700": "55, 65, 81",    "800": "31, 41, 55",
                "900": "17, 24, 39",   "950": "3, 7, 18",
            },
            "primary": {
                "50": "250, 245, 255", "100": "243, 232, 255", "200": "233, 213, 255",
                "300": "216, 180, 254","400": "192, 132, 252", "500": "168, 85, 247",
                "600": "147, 51, 234", "700": "126, 34, 206",  "800": "107, 33, 168",
                "900": "88, 28, 135",  "950": "59, 7, 100",
            },
            "font": {
                "subtle-light": "var(--color-base-500)", "subtle-dark": "var(--color-base-400)",
                "default-light": "var(--color-base-600)","default-dark": "var(--color-base-300)",
                "important-light": "var(--color-base-900)","important-dark": "var(--color-base-100)",
            },
        },
    ),
    "SCRIPTS": settings.get("ADMIN_SCRIPTS", [
        lambda request: static("js/vendors.js"),
        lambda request: static("js/project.js"),
    ]),
    "STYLES": settings.get("ADMIN_STYLES", [
        lambda request: static("css/admin.css"),
    ]),
    "ENVIRONMENT_CALLBACK": settings.get("ADMIN_ENVIRONMENT_CALLBACK", None),
    "DASHBOARD_CALLBACK": settings.get("ADMIN_DASHBOARD_CALLBACK", None),
    "THEME": settings.get("ADMIN_THEME", "default"),
}

# ADMIN_TEMPLATE is an alias — Unfold IS the admin template
ADMIN_TEMPLATE = UNFOLD

# -------------------------------
# Admin Site Class
# -------------------------------
ADMIN_SITE_CLASS = settings.get("ADMIN_SITE_CLASS", "django.contrib.admin.AdminSite")

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
    "SESSION_TIMEOUT": settings.get("ADMIN_SESSION_TIMEOUT", 120),
    "MAX_LOGIN_ATTEMPTS": settings.get("ADMIN_MAX_LOGIN_ATTEMPTS", 5),
    "LOCKOUT_TIME": settings.get("ADMIN_LOCKOUT_TIME", 15),
    "REQUIRE_2FA": settings.get("ADMIN_REQUIRE_2FA", settings.is_production),
    "IP_WHITELIST": settings.get("ADMIN_IP_WHITELIST", []),
}

# -------------------------------
# Admin Logging
# -------------------------------
ADMIN_LOGGING = {
    "ENABLED": settings.get("ADMIN_LOGGING_ENABLED", True),
    "LEVEL": settings.get("ADMIN_LOGGING_LEVEL", "INFO"),
    "FORMAT": "json" if settings.is_production else "verbose",
    "MAX_SIZE": settings.get("ADMIN_LOG_MAX_SIZE", 10 * 1024 * 1024),
    "BACKUP_COUNT": settings.get("ADMIN_LOG_BACKUP_COUNT", 5),
}

# -------------------------------
# Wagtail Transfer Configuration
# -------------------------------
WAGTAILTRANSFER_SECRET_KEY = settings.get("WAGTAILTRANSFER_SECRET_KEY", "")
WAGTAILTRANSFER_SOURCES = settings.get("WAGTAILTRANSFER_SOURCES", {})
WAGTAILTRANSFER_UPDATE_RELATED_MODELS = settings.get(
    "WAGTAILTRANSFER_UPDATE_RELATED_MODELS",
    ["wagtailimages.image", "wagtaildocs.document"],
)

if settings.is_production:
    WAGTAILTRANSFER_SECRET_KEY = settings.get("WAGTAILTRANSFER_SECRET_KEY_PROD", "ea3ea7cd5daeaf8ea36a7cd5dc2ada7e")
    WAGTAILTRANSFER_SOURCES = settings.get(
        "WAGTAILTRANSFER_SOURCES_PROD",
        {"demo": {"BASE_URL": "https://demo.structa.cloud/wagtail-transfer/", "SECRET_KEY": "4ac4822773be75eea36b21a47273b2ae"}},
    )
else:
    WAGTAILTRANSFER_SECRET_KEY = settings.get("WAGTAILTRANSFER_SECRET_KEY_DEV", "4ac4822773be75eea36b21a47273b2ae")
    WAGTAILTRANSFER_SOURCES = settings.get(
        "WAGTAILTRANSFER_SOURCES_DEV",
        {"main": {"BASE_URL": "https://www.structa.cloud/wagtail-transfer/", "SECRET_KEY": "ea3ea7cd5daeaf8ea36a7cd5dc2ada7e"}},
    )
