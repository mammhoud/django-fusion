"""Template context processors — the language catalog for every template.

Exposes the seeded ``SiteLanguage`` snippet (or a static mirror before the
first ``seed_pages`` run) so templates never hardcode language codes, native
names, flags, or directions. Direction derives from the catalog's ``dir``
field — the same source the switcher and the ``/apis/content/languages/``
endpoint consume — instead of literal ``dir="rtl"`` guards.

The JSON variants are plain strings: ``{{ fusion_languages_json }}`` renders
autoescaped inside an ``x-data`` attribute (entities decode back to real
quotes), while ``{{ fusion_language_dirs_json|safe }}`` is for raw ``<script>``
content where HTML entities would be a JS syntax error.
"""

from __future__ import annotations

import json

# Static mirror of DEFAULT_SITE_LANGUAGES so every template still renders
# before ``seed_pages`` runs (fresh DB / first boot).
_FALLBACK_LANGUAGES = [
    {"code": "en", "native": "English", "flag": "🇬🇧", "dir": "ltr"},
    {"code": "ar", "native": "العربية", "flag": "🇸🇦", "dir": "rtl"},
    {"code": "sv", "native": "Svenska", "flag": "🇸🇪", "dir": "ltr"},
    {"code": "fr", "native": "Français", "flag": "🇫🇷", "dir": "ltr"},
    {"code": "de", "native": "Deutsch", "flag": "🇩🇪", "dir": "ltr"},
    {"code": "es", "native": "Español", "flag": "🇪🇸", "dir": "ltr"},
    {"code": "pt", "native": "Português", "flag": "🇧🇷", "dir": "ltr"},
]


def _site_languages() -> list[dict]:
    try:
        from .models.languages import SiteLanguage

        rows = list(SiteLanguage.active().order_by("sort_order", "code"))
        if rows:
            return [row.as_dict() for row in rows]
    except Exception:
        pass
    return [dict(item) for item in _FALLBACK_LANGUAGES]


def fusion_languages(request):
    """Attach the language catalog + direction map to the template context."""
    languages = _site_languages()
    return {
        "fusion_languages": languages,
        "fusion_languages_json": json.dumps(languages, ensure_ascii=False),
        "fusion_language_dirs_json": json.dumps(
            {item["code"]: item["dir"] for item in languages},
            ensure_ascii=False,
        ),
    }
