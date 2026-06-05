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
]

LOCAL_APPS = [
    # Website-local infrastructure. www.core exposes shared management commands
    # such as setup_wagtail_home without importing legacy duplicated models.
    "www.core",
    # django_rseal must be in INSTALLED_APPS so its GenericSetting models
    # (EmailSettings, Newsletter, etc.) can register with Wagtail.
    "django_rseal",
    # CTC page/LMS models are required by the bundled Wagtail fixtures.
    "www.core.content.apps.ContentConfig",
    "plugins.accounts.apps.AccountsConfig",
    "plugins.lms.apps.LmsConfig",
    # Legacy page apps are optional; AppRegistry filters them when absent.
    "pages.home",
    "pages.about",
    "pages.cv",
    "pages.connect",
    "pages.portfolio",
    "pages.blog",
]


OPTIONAL_APP_MAP = {}

_registry = AppRegistry()
EFFECTIVE_THIRD_PARTY_APPS = _registry.available_apps(THIRD_PARTY_APPS)
EFFECTIVE_LOCAL_APPS = _registry.available_apps(LOCAL_APPS)

INSTALLED_APPS: list[str] = AppRegistry.merge(
    APPS,
    EFFECTIVE_WAGTAIL_APPS,
    EFFECTIVE_THIRD_PARTY_APPS,
    EFFECTIVE_LOCAL_APPS,
)
