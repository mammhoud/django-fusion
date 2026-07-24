"""
i18n API endpoints for the LMS frontend.

Provides language switching and listing so the Next.js frontend can
switch the active language without a full page reload (SPA-friendly).
"""

import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import activate

logger = logging.getLogger(__name__)


def language_list(request):
    """GET /apis/i18n/languages/ — list available languages and the active one.

    Returns:
        {
            "languages": [{"code": "en", "name": "English"}, ...],
            "current": "en"
        }
    """
    current = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
    return JsonResponse(
        {
            "languages": [
                {"code": code, "name": str(name)} for code, name in settings.LANGUAGES
            ],
            "current": current,
        }
    )


def set_language_view(request):
    """POST /apis/i18n/setlang/ — switch the active language via JSON.

    Accepts JSON body: ``{"language": "fr"}``.

    Returns:
        {"status": "ok", "language": "fr"}

    The language is activated on the server side for this request and
    persisted via a ``django_language`` cookie so subsequent requests
    inherit the choice.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        import json

        body = json.loads(request.body.decode("utf-8"))
        lang = body.get("language", "").strip()
    except (json.JSONDecodeError, UnicodeDecodeError):
        lang = request.POST.get("language", "").strip()

    if not lang:
        return JsonResponse({"error": "Missing 'language' field"}, status=400)

    # Validate against known languages
    known = {code for code, _name in settings.LANGUAGES}
    if lang not in known:
        return JsonResponse(
            {"error": f"Unknown language '{lang}'", "available": list(known)},
            status=400,
        )

    activate(lang)
    response = JsonResponse({"status": "ok", "language": lang})

    # Set the django_language cookie so LocaleMiddleware picks it up
    cookie_kwargs = {
        "max_age": getattr(settings, "LANGUAGE_COOKIE_AGE", 60 * 60 * 24 * 365),
        "path": getattr(settings, "LANGUAGE_COOKIE_PATH", "/"),
        "domain": getattr(settings, "LANGUAGE_COOKIE_DOMAIN", None),
        "secure": getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
        "httponly": getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
        "samesite": getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
    }
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        **{k: v for k, v in cookie_kwargs.items() if v is not None},
    )

    return response
