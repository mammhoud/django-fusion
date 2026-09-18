"""Locale preference API for the Loop-CRM shell.

The Astro shell is static, while Django owns the active locale for navigation
fragments and other server-rendered surfaces. This small JSON contract lets the
shell discover the supported languages and persist a user's choice in the
standard Django language cookie without introducing a second i18n dependency.
"""
from __future__ import annotations

import json

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.middleware.csrf import get_token
from django.utils.translation import activate, get_language, gettext
from django.views.decorators.http import require_http_methods


def _languages() -> list[dict[str, str]]:
    return [
        {
            "code": code,
            "label": str(label),
            "direction": "rtl" if code.split("-", 1)[0] in {"ar", "fa", "he", "ur"} else "ltr",
        }
        for code, label in settings.LANGUAGES
    ]


@require_http_methods(["GET", "POST"])
def locale_api(request: HttpRequest) -> JsonResponse:
    """Read or persist the current interface locale.

    ``POST`` is intentionally same-origin and CSRF-protected by Django's
    middleware. The response only contains locale metadata; it never accepts
    arbitrary translation paths or executes user-provided language settings.
    """
    supported = {item["code"] for item in _languages()}
    if request.method == "POST":
        try:
            payload = json.loads(request.body or b"{}")
        except (TypeError, ValueError):
            return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
        code = str(payload.get("language") or "").strip().lower()
        if code not in supported:
            return JsonResponse(
                {"language": "Choose one of the supported interface languages."}, status=400
            )
        activate(code)
        response = JsonResponse(
            {"current": code, "direction": "rtl" if code == "ar" else "ltr", "languages": _languages()}
        )
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            code,
            max_age=getattr(settings, "LANGUAGE_COOKIE_AGE", None),
            secure=not settings.DEBUG,
            httponly=False,
            samesite="Lax",
        )
        return response

    current = (get_language() or settings.LANGUAGE_CODE).split("-", 1)[0]
    # Ensure the static shell receives a CSRF cookie before its first locale
    # mutation; this does not expose the token in the JSON response.
    get_token(request)
    return JsonResponse(
        {
            "current": current,
            "direction": "rtl" if current == "ar" else "ltr",
            "languages": _languages(),
            "label": gettext("Interface language"),
        }
    )
