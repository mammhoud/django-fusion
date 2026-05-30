import importlib



# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    # Cookie & Theme Middleware
    "core.middleware.CookieConsentMiddleware",
    "core.middleware.ThemeMiddleware",
    "core.middleware.MediaRequestLoggingMiddleware",
    # "django.contrib.auth.middleware.LoginRequiredMiddleware",
    # "core.middlewares.language.DefaultLanguageMiddleware",
]


def _middleware_available(path: str) -> bool:
    if path.startswith("django."):
        return True
    module_name, _, class_name = path.rpartition(".")
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return hasattr(module, class_name)


MIDDLEWARE = [middleware for middleware in MIDDLEWARE if _middleware_available(middleware)]
