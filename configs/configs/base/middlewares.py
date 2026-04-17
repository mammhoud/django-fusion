

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    # "django.contrib.auth.middleware.LoginRequiredMiddleware",
    # "allauth.usersessions.middleware.UserSessionsMiddleware",
    # "src.utils.middlewares.htmx.HtmxMiddleware",
    # "django_htmx.middleware.HtmxMiddleware",
    "django_rseal.pipelines.middlewares.SiteMiddleware",
    # "core.middlewares.language.DefaultLanguageMiddleware",
]
