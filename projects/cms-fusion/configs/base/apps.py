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

APPS = [*DJANGO_APPS, *EFFECTIVE_ADMIN_APPS]

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
    "webpack_loader",
    "django_htmx",
    "import_export",
    "simple_history",
    "django_extensions",
    "heroicons",
    "embed_video",
    "colorfield",
    "django_rq",
    "django_celery_beat",
    "django_celery_results",
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
#   projects/ctc-research/settings.py
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
    ["www.worker"],
)
# Per-site LOCAL_APPS are appended by each website's settings.py after
# the `from configs.settings import *` line.
