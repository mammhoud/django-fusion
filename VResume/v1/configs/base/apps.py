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
APPS = [
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    *ADMIN_APPS,
    "django.contrib.admin",
    "django.forms",
    "django.contrib.postgres",
]

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
    "pages.home",     # HomePage + Slider, TeamMember, Service, Testimonial, VResumeSettings
    "pages.about",    # AboutPage
    "pages.cv",       # ResumePage
    "pages.connect",  # ContactPage + Campaign, Subscriber, FormSubmission, ...
    "pages.portfolio",# PortfolioPage + Project, PortfolioTag
    "pages.blog",     # BlogPage + BlogIndexPage + snippets
]

# COMBINED
INSTALLED_APPS: list[str] = APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + LOCAL_APPS
