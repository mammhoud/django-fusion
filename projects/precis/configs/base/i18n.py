# ====================================
# 🌍 Internationalization & Localization
# ====================================
from django.utils.translation import gettext_lazy as _

from ..settings.conf import Environment, settings
from .paths import BASE_DIR

# -------------------------------
# Time & Locale Configuration
# -------------------------------
USE_I18N = settings.get("USE_I18N", True)
USE_L10N = settings.get("USE_L10N", True)
USE_TZ = settings.get("USE_TZ", True)

# Locale paths
LOCALE_PATHS = settings.get(
    "LOCALE_PATHS",
    [
        str(BASE_DIR / "locale"),
        str(BASE_DIR / "assets" / "locale"),
    ],
)

# Time zone configuration
TIME_ZONE = settings.get("TIME_ZONE", "UTC")
if settings.SERVER_ENV.value in ["demo", "development"]:
    # Use local timezone for development/demo
    TIME_ZONE = settings.get("LOCAL_TIME_ZONE", "Africa/Cairo")

# -------------------------------
# Language Configuration
# -------------------------------
LANGUAGE_CODE = settings.get("LANGUAGE_CODE", "en")
# Shared django-fusion language contract. Sites may narrow this catalog through
# their Wagtail SiteLanguage snippets, but Django's base settings remain the
# validation source for middleware, cookies, sessions, and translations.
FUSION_LANGUAGES = settings.get(
    "FUSION_LANGUAGES",
    [
        ("en", _("English")),
        ("ar", _("Arabic")),
        ("sv", _("Swedish")),
        ("fr", _("French")),
        ("de", _("German")),
        ("es", _("Spanish")),
        ("pt", _("Portuguese")),
        ("pt-br", _("Portuguese (Brazil)")),
    ],
)
# Session key used by products that persist the language alongside Django's
# language cookie. Django's stock set_language view does not define this
# setting, so keep the shared default explicit for middleware/API consumers.
LANGUAGE_SESSION_KEY = settings.get("LANGUAGE_SESSION_KEY", "_language")
LANGUAGE_COOKIE_NAME = settings.get("LANGUAGE_COOKIE_NAME", "django_language")
LANGUAGE_COOKIE_AGE = settings.get("LANGUAGE_COOKIE_AGE", 60 * 60 * 24 * 365)  # 1 year
LANGUAGE_COOKIE_DOMAIN = settings.get("LANGUAGE_COOKIE_DOMAIN", None)
LANGUAGE_COOKIE_PATH = settings.get("LANGUAGE_COOKIE_PATH", "/")
LANGUAGE_COOKIE_SECURE = settings.get("LANGUAGE_COOKIE_SECURE", settings.is_production)
LANGUAGE_COOKIE_HTTPONLY = settings.get("LANGUAGE_COOKIE_HTTPONLY", False)
LANGUAGE_COOKIE_SAMESITE = settings.get("LANGUAGE_COOKIE_SAMESITE", "Lax")

# -------------------------------
# Available Languages
# -------------------------------
LANGUAGES = settings.get("LANGUAGES", FUSION_LANGUAGES)

# Language BiDi support (right-to-left languages)
LANGUAGES_BIDI = settings.get("LANGUAGES_BIDI", ["ar", "he", "fa", "ur"])

# Default language bi-directionality
LANGUAGE_BIDI = LANGUAGE_CODE in LANGUAGES_BIDI

# -------------------------------
# Translation Files
# -------------------------------
TRANSLATION_FILES = {
    "django": ["django"],
    "djangojs": ["django"],
    "wagtail": ["wagtail"],
    "app": ["core", "apps"],
}

# -------------------------------
# Wagtail Internationalization
# -------------------------------
WAGTAIL_I18N_ENABLED = settings.get("WAGTAIL_I18N_ENABLED", True)
WAGTAIL_CONTENT_LANGUAGES = settings.get("WAGTAIL_CONTENT_LANGUAGES", LANGUAGES)

# Wagtail Locale model configuration
WAGTAIL_I18N_LOCALE_MODEL = "wagtailcore.Locale"

# -------------------------------
# Format Localization
# -------------------------------
# Decimal and thousand separator
DECIMAL_SEPARATOR = settings.get("DECIMAL_SEPARATOR", ".")
THOUSAND_SEPARATOR = settings.get("THOUSAND_SEPARATOR", ",")

# Date & Time formats
DATE_FORMAT = settings.get("DATE_FORMAT", "N j, Y")
TIME_FORMAT = settings.get("TIME_FORMAT", "P")
DATETIME_FORMAT = settings.get("DATETIME_FORMAT", "N j, Y, P")
YEAR_MONTH_FORMAT = settings.get("YEAR_MONTH_FORMAT", "F Y")
MONTH_DAY_FORMAT = settings.get("MONTH_DAY_FORMAT", "F j")
SHORT_DATE_FORMAT = settings.get("SHORT_DATE_FORMAT", "m/d/Y")
SHORT_DATETIME_FORMAT = settings.get("SHORT_DATETIME_FORMAT", "m/d/Y P")

# First day of week (0=Sunday, 1=Monday)
FIRST_DAY_OF_WEEK = settings.get("FIRST_DAY_OF_WEEK", 0)

# -------------------------------
# Number Formatting
# -------------------------------
NUMBER_GROUPING = settings.get("NUMBER_GROUPING", 3)
USE_THOUSAND_SEPARATOR = settings.get("USE_THOUSAND_SEPARATOR", True)

# -------------------------------
# Translation Backend
# -------------------------------
TRANSLATION_BACKEND = settings.get("TRANSLATION_BACKEND", "django.utils.translation.real")

# -------------------------------
# Localization Middleware
# -------------------------------
LOCALE_MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",
]

# -------------------------------
# Language Detection
# -------------------------------
LANGUAGE_DETECTION = {
    "ENABLED": settings.get("LANGUAGE_DETECTION_ENABLED", True),
    "FROM_PATH": settings.get("LANGUAGE_FROM_PATH", True),
    "FROM_USER": settings.get("LANGUAGE_FROM_USER", True),
    "FROM_SESSION": settings.get("LANGUAGE_FROM_SESSION", True),
    "FROM_COOKIE": settings.get("LANGUAGE_FROM_COOKIE", True),
    "FROM_HEADER": settings.get("LANGUAGE_FROM_HEADER", True),
}

# -------------------------------
# Bilingual Support
# -------------------------------
BILINGUAL_SUPPORT = {
    "ENABLED": settings.get("BILINGUAL_SUPPORT_ENABLED", True),
    "DEFAULT_LANGUAGE": LANGUAGE_CODE,
    "FALLBACK_LANGUAGES": settings.get("FALLBACK_LANGUAGES", ["en"]),
    "AUTO_TRANSLATE": settings.get("AUTO_TRANSLATE", False),
}

# -------------------------------
# RTL (Right-to-Left) Support
# -------------------------------
RTL_SUPPORT = {
    "ENABLED": settings.get("RTL_SUPPORT_ENABLED", True),
    "LANGUAGES": LANGUAGES_BIDI,
    "CSS_CLASS": "rtl",
    "TEXT_DIRECTION": "rtl",
}
