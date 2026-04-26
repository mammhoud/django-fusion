# UNFOLD — must be listed before django.contrib.admin
UNFOLD_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
]

# DJANGO CORE
APPS = [
    # "daphne",
    *UNFOLD_APPS,
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


# ADMIN (legacy alias kept for compatibility)
ADMIN_APPS = [
    *UNFOLD_APPS,
]


# WAGTAIL
WAGTAIL_APPS = [
    "wagtail",
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
    # "django_rseal.pipelines",  # deprecated shim — no models needed
    "django_osoul.comp",
    # "django_rseal.mcp_designer",  # optional MCP tooling
    "django_rseal.email",
    "django_rseal",  # required for DefaultBase, Coupon, Newsletter and other shared models
    "plugins.accounts",  # Service, Organization, Team models + registration
    "plugins.lms",       # LMS: Course, Lesson, Module, Enrollment, Certificate
    "plugins.profile",  # Profile, Dashboard, Settings
    "plugins.products",  # Cart, CartItem, Checkout
]


OVERRIDE_APPS = [
    # "apps.content",      # TODO: create this app
]


LOCAL_APPS = [
    "www.core",  # provides setup_wagtail_home management command (no migrations)
    # "core.CI",   # TODO: create this app
    # "apps.lms",  # TODO: create this app
    # "apps.blog", # TODO: create this app
]

# COMBINED
INSTALLED_APPS: list[str] = OVERRIDE_APPS + APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + PLUGIN_APPS + LOCAL_APPS
