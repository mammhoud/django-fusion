# DJANGO CORE
APPS = [
    # "daphne",
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


# ADMIN
ADMIN_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
]


# WAGTAIL
WAGTAIL_APPS = [
    "wagtail",
    *ADMIN_APPS,
    # "wagtail.api.v2",
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
    "wagtail_newsletter",
    "wagtailfontawesomesvg",
    "taggit",
    "modelcluster",
]
THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.linkedin_oauth2",
    "webpack_loader",
    "django_htmx",
    "import_export",
    "simple_history",
    "django_extensions",
    "django_structlog",
    "heroicons",
    "embed_video",
    "colorfield",  # Color picker field for Wagtail
    "django_rq",
]


PLUGIN_APPS = [
    "django_rseal.pipelines",
    "django_osoul.comp",
    "django_rseal.mcp_designer",
]


OVERRIDE_APPS = [
    "apps.pages",
    "apps.handlers",
    "apps.handlers.registration",
]


LOCAL_APPS = [
    "alliance.CI",
    "alliance",
]

# COMBINED
INSTALLED_APPS: list[str] = OVERRIDE_APPS + APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + PLUGIN_APPS + LOCAL_APPS


# "guardian",
# "polymorphic",

# "django_celery_beat",
# "django_q",
# "django_q_registry",
# "django_tailwind_cli",
# "django_filters",
# "django_tables2",
# "ninja_extra",
# "ninja_jwt",

# "corsheaders",
# "djmoney",
# "schema_viewer",
# "django_cotton.apps.SimpleAppConfig",
# "colorfield",
# "wagtail_transfer",
# "components",
# "crispy_forms",
# "crispy_tailwind",
# "widget_tweaks",


