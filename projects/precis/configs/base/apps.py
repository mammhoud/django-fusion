"""Application registry for workspace websites.

Keeps canonical app lists explicit while allowing optional package filtering
for local/container environments where some integrations may be unavailable.
"""

from configs.base.classes import AppRegistry

# ADMIN
ADMIN_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.simple_history",
]
EFFECTIVE_ADMIN_APPS = AppRegistry().available_apps(ADMIN_APPS)

# DJANGO CORE
DJANGO_APPS = [
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.forms",
]

if AppRegistry().has_any("psycopg", "psycopg2"):
    DJANGO_APPS.append("django.contrib.postgres")


def _admin_theme_first(django_apps: list[str], admin_apps: list[str]) -> list[str]:
    """Insert the admin-theme apps (unfold + contrib) before django.contrib.admin.

    unfold ships themed overrides of two Django admin static files
    (admin/js/actions.js, admin/js/admin/RelatedObjectLookups.js). For its
    versions to be the ones collectstatic keeps, unfold must precede
    ``django.contrib.admin`` in INSTALLED_APPS.
    """
    apps = list(django_apps)
    anchor = "django.contrib.admin"
    if anchor in apps:
        idx = apps.index(anchor)
        apps[idx:idx] = admin_apps
    else:
        apps[:0] = admin_apps
    return apps


APPS = _admin_theme_first(DJANGO_APPS, EFFECTIVE_ADMIN_APPS)

# WAGTAIL
WAGTAIL_APPS = [
    "wagtail",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.sitemaps",
    "wagtail.contrib.settings",
    "wagtail.contrib.frontend_cache",
    "wagtail.contrib.simple_translation",
    "wagtail.contrib.styleguide",
    "wagtail.contrib.table_block",
    "wagtail.contrib.typed_table_block",
    "wagtail.documents",
    "wagtail.embeds",
    "wagtail.images",
    "wagtail.search",
    "wagtail.snippets",
    "wagtail.sites",
    "wagtail.admin",
    "wagtail.users",
    "wagtail.locales",
    "taggit",
    "modelcluster",
]

EFFECTIVE_WAGTAIL_APPS = AppRegistry().available_apps(WAGTAIL_APPS)

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "webpack_loader",
    "django_htmx",
    "import_export",
    "simple_history",
    "django_extensions",
    "heroicons",
    "embed_video",
    "colorfield",
    "django_dramatiq",
]

# Local shared libraries developed alongside the workspace.
# These are filtered by availability so the base config remains usable
# when a library is not installed in a given environment.
LOCAL_LIBRARY_APPS = [
    "django_fusion",
]

# ── LOCAL_APPS ──────────────────────────────────────────────────────
# Each website defines its own LOCAL_APPS in its site-level settings.py
# because each site ships a different set of plugins, page apps, and
# www sub-packages.  See:
#   projects/fusion-cms/settings.py
#   projects/lms/settings.py
#   projects/portfolio/settings.py

OPTIONAL_APP_MAP = {}

_registry = AppRegistry()
EFFECTIVE_THIRD_PARTY_APPS = _registry.available_apps(THIRD_PARTY_APPS)
EFFECTIVE_LOCAL_LIBRARY_APPS = _registry.available_apps(LOCAL_LIBRARY_APPS)

INSTALLED_APPS: list[str] = AppRegistry.merge(
    APPS,
    EFFECTIVE_WAGTAIL_APPS,
    EFFECTIVE_LOCAL_LIBRARY_APPS,
    EFFECTIVE_THIRD_PARTY_APPS,
)
# Precis app-specific entries are appended by backend/settings.py after
# the `from configs.default import *` line.
