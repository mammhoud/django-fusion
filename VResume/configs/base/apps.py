"""Application registry for workspace websites.

Keeps canonical app lists explicit while allowing optional package filtering
for local/container environments where some integrations may be unavailable.
"""

import importlib.util as _ilu

# ADMIN
ADMIN_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.simple_history",
]

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
    "django.contrib.postgres",
]

APPS = [*DJANGO_APPS, *ADMIN_APPS]

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

THIRD_PARTY_APPS = [
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
    "pages.home",
    "pages.about",
    "pages.cv",
    "pages.connect",
    "pages.portfolio",
    "pages.blog",
]


def _is_mod(name: str) -> bool:
    try:
        return _ilu.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


OPTIONAL_APP_MAP = {
    "django_celery_beat": "django_celery_beat",
    "django_celery_results": "django_celery_results",
    "django_rq": "django_rq",
    "simple_history": "simple_history",
    "import_export": "import_export",
    "webpack_loader": "webpack_loader",
}

EFFECTIVE_THIRD_PARTY_APPS = [
    app for app in THIRD_PARTY_APPS if _is_mod(OPTIONAL_APP_MAP.get(app, app))
]
EFFECTIVE_LOCAL_APPS = [app for app in LOCAL_APPS if _is_mod(app)]

INSTALLED_APPS: list[str] = APPS + WAGTAIL_APPS + EFFECTIVE_THIRD_PARTY_APPS + EFFECTIVE_LOCAL_APPS
