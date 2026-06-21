from django.conf import settings
from django.utils import translation


def LANGUAGES(request=None):  # noqa: ARG001
    """
    Unified helper to gather language information for Wagtail + Django.

    Returns:
        {
            "LANGUAGES": [...],
            "LANGUAGE_CODE": "en"
        }
    """
    languages = []

    # Current + default language
    current_language = translation.get_language() or settings.LANGUAGE_CODE
    default_language = getattr(settings, "LANGUAGE_CODE", "en")

    # Get configured languages (Wagtail > Django)
    content_languages = getattr(
        settings,
        "WAGTAIL_CONTENT_LANGUAGES",
        getattr(settings, "LANGUAGES", []),
    )

    # Use all configured languages as active (pure Django fallback)
    active_locale_codes = [code for code, _ in content_languages]

    # Build final languages list
    for code, name in content_languages:
        info = translation.get_language_info(code)
        languages.append({
            "code": code,
            "name": name,
            "url": f"/{code}/",
            "name_local": info.get("name_local", name),
            "is_active": code in active_locale_codes,
            "is_current": code == current_language,
            "is_default": code == default_language,
        })

    return {
        "LANGUAGES": languages,
        "LANGUAGE_CODE": current_language,
    }
