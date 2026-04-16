# ====================================
# 🌿 Wagtail Configuration
# ====================================
from ..settings.conf import settings

# -------------------------------
# Core Wagtail Settings
# -------------------------------
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "Structa")
WAGTAILADMIN_BASE_URL = settings.get("WAGTAILADMIN_BASE_URL", "https://structa.cloud")
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAIL_PASSWORD_MANAGEMENT_ENABLED = True
WAGTAIL_PASSWORD_RESET_ENABLED = True

# -------------------------------
# Wagtail i18n
# -------------------------------
WAGTAIL_I18N_ENABLED = settings.get("WAGTAIL_I18N_ENABLED", True)
WAGTAIL_CONTENT_LANGUAGES = settings.get(
    "WAGTAIL_CONTENT_LANGUAGES",
    [
        ("en", "English"),
        ("ar", "Arabic"),
    ],
)

# -------------------------------
# Wagtail Search
# -------------------------------
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# -------------------------------
# Wagtail Images
# -------------------------------
WAGTAILIMAGES_IMAGE_MODEL = settings.get("WAGTAILIMAGES_IMAGE_MODEL", "wagtailimages.Image")
WAGTAILIMAGES_MAX_UPLOAD_SIZE = settings.get("WAGTAILIMAGES_MAX_UPLOAD_SIZE", 10 * 1024 * 1024)  # 10MB
WAGTAILIMAGES_SERVE_METHOD = settings.get("WAGTAILIMAGES_SERVE_METHOD", "direct")
WAGTAILEMBEDS_RESPONSIVE_HTML = True

# -------------------------------
# Wagtail Documents
# -------------------------------
WAGTAILDOCS_DOCUMENT_MODEL = settings.get("WAGTAILDOCS_DOCUMENT_MODEL", "wagtaildocs.Document")

# -------------------------------
# Wagtail Cache
# -------------------------------
WAGTAIL_CACHE = settings.get("WAGTAIL_CACHE", False)
WAGTAIL_CACHE_BACKEND = settings.get("WAGTAIL_CACHE_BACKEND", "default")

# -------------------------------
# Wagtail Rich Text
# -------------------------------
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {
        "WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea",
        "OPTIONS": {
            "features": [
                "h2", "h3", "h4", "bold", "italic", "link",
                "ol", "ul", "hr", "blockquote", "image", "embed",
            ]
        },
    }
}

# -------------------------------
# Root Page = HomePage (set via DB signal / management command)
# The actual DB-level root page assignment is handled by the
# `setup_wagtail_home` management command run at container startup.
# -------------------------------
WAGTAIL_ROOT_PAGE_MODEL = "pages.HomePage"
