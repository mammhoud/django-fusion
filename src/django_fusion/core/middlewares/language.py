"""Shared Django/Wagtail language preference contract.

The contract is deliberately site-agnostic:

* query ``?lang=``/``?language=`` is a request-scoped override;
* the Django session is the durable server-side preference;
* the configured language cookie keeps non-API requests and static shells aligned;
* the active middleware language and ``Accept-Language`` are negotiation inputs;
* ``settings.LANGUAGE_CODE`` is the final default.

Product APIs should call :func:`resolve_language` instead of implementing a
second cookie/header parser. Wagtail content selection remains product-owned,
but it receives one normalized code from this module.
"""

from __future__ import annotations

from collections.abc import Iterable

from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import activate
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST


def _language_pairs() -> list[tuple[str, str]]:
    """Return configured Django/Wagtail language pairs without duplicates."""
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    sources = (
        getattr(settings, "FUSION_LANGUAGES", ()),
        getattr(settings, "WAGTAIL_CONTENT_LANGUAGES", ()),
        getattr(settings, "LANGUAGES", ()),
    )
    for source in sources:
        for item in source or ():
            try:
                code, label = item
            except (TypeError, ValueError):
                continue
            normalized = str(code).strip().lower().replace("_", "-")
            if normalized and normalized not in seen:
                seen.add(normalized)
                pairs.append((normalized, str(label)))
    return pairs


def configured_language_codes() -> tuple[str, ...]:
    """Return the ordered language codes configured by the active site."""
    return tuple(code for code, _label in _language_pairs())


def normalize_language(value: object, supported: Iterable[str] | None = None) -> str | None:
    """Normalize a BCP-47-ish value to one configured language code.

    Exact regional codes such as ``pt-br`` are preserved. A base code such as
    ``pt`` is accepted only when it is configured directly or maps to one
    unambiguous regional variant; this avoids silently turning ``pt-br`` into
    ``pt`` in CTC's Wagtail fixture tree.
    """
    candidate = str(value or "").strip().lower().replace("_", "-")
    if not candidate:
        return None
    codes = tuple(supported or configured_language_codes())
    if candidate in codes:
        return candidate
    base = candidate.split("-")[0]
    variants = [code for code in codes if code.split("-")[0] == base]
    return variants[0] if len(variants) == 1 else None


def _query_language(request) -> str | None:
    return normalize_language(request.GET.get("lang") or request.GET.get("language"))


def _session_language(request) -> str | None:
    session = getattr(request, "session", None)
    if session is None:
        return None
    return normalize_language(session.get(language_session_key()))


def _cookie_language(request) -> str | None:
    return normalize_language(
        request.COOKIES.get(getattr(settings, "LANGUAGE_COOKIE_NAME", "django_language"))
    )


def _header_language(request) -> str | None:
    header = request.headers.get("Accept-Language", "")
    # Parse in client order. Django's LocaleMiddleware already handles q
    # weights; this is only used when that middleware is not present.
    for item in header.split(","):
        code = item.split(";", 1)[0].strip()
        language = normalize_language(code)
        if language:
            return language
    return None


def language_session_key() -> str:
    """Return the configured session key shared by all sites."""
    return str(getattr(settings, "LANGUAGE_SESSION_KEY", "_language"))


def language_cookie_name() -> str:
    return str(getattr(settings, "LANGUAGE_COOKIE_NAME", "django_language"))


def language_cookie_kwargs() -> dict[str, object]:
    """Return Django's configured cookie attributes for language responses."""
    return {
        "max_age": getattr(settings, "LANGUAGE_COOKIE_AGE", 60 * 60 * 24 * 365),
        "path": getattr(settings, "LANGUAGE_COOKIE_PATH", "/"),
        "domain": getattr(settings, "LANGUAGE_COOKIE_DOMAIN", None),
        "secure": getattr(settings, "LANGUAGE_COOKIE_SECURE", not getattr(settings, "DEBUG", False)),
        "httponly": getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", False),
        "samesite": getattr(settings, "LANGUAGE_COOKIE_SAMESITE", "Lax"),
    }


def resolve_language(request) -> str:
    """Resolve the request language using one stable priority order."""
    default = normalize_language(getattr(settings, "LANGUAGE_CODE", "en"))
    codes = configured_language_codes()
    default = default or (codes[0] if codes else "en")
    return (
        _query_language(request)
        or _session_language(request)
        or _cookie_language(request)
        or normalize_language(getattr(request, "LANGUAGE_CODE", None))
        or _header_language(request)
        or default
    )


def persist_language(request, response, language: str, *, save_session: bool = True):
    """Persist a validated language in the session and configured cookie."""
    normalized = normalize_language(language)
    if normalized is None:
        return response
    session = getattr(request, "session", None)
    if save_session and session is not None:
        session[language_session_key()] = normalized
        session.modified = True
    activate(normalized)
    response.set_cookie(language_cookie_name(), normalized, **language_cookie_kwargs())
    return response


class DefaultLanguageMiddleware:
    """Activate and persist the shared Django/Wagtail language preference."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = resolve_language(request)
        explicit = _query_language(request)
        session_language = _session_language(request)
        cookie_language = _cookie_language(request)

        # LocaleMiddleware may have run earlier, but APIs and serializers also
        # read request.LANGUAGE_CODE. Keep both translation state and request
        # metadata aligned for every rendering road.
        activate(language)
        request.LANGUAGE_CODE = language
        response = self.get_response(request)

        # A cookie or explicit/session choice is durable. The default is not
        # written until the user chooses a language, avoiding a false choice
        # in a fresh browser while still refreshing malformed/missing cookies.
        #
        # When the session already carries the resolved language (e.g. the
        # set_language_api wrote it in the same request), skip re-persistence
        # so the view's cookie is not overwritten by a stale request-level
        # cookie value.
        session_already_set = session_language == language
        if not session_already_set and (
            explicit or session_language or cookie_language or language_cookie_name() not in request.COOKIES
        ):
            persist_language(request, response, language, save_session=bool(explicit or session_language or cookie_language))
        return response


@require_POST
@csrf_protect
def set_language_api(request):
    """POST endpoint shared by Astro, HTMX, and server-rendered switchers."""
    language = normalize_language(request.POST.get("language"))
    if language is None:
        return JsonResponse(
            {
                "error": "Unsupported language",
                "language": resolve_language(request),
                "available_languages": list(configured_language_codes()),
            },
            status=400,
        )

    # Persist in session *before* returning so the DefaultLanguageMiddleware
    # sees a durable session language and does not overwrite the cookie with
    # the stale request-level value.
    session = getattr(request, "session", None)
    if session is not None:
        session[language_session_key()] = language
        session.modified = True
    response = JsonResponse(
        {
            "language": language,
            "default_language": normalize_language(getattr(settings, "LANGUAGE_CODE", "en")) or "en",
            "session_key": language_session_key(),
            "cookie_name": language_cookie_name(),
            "available_languages": list(configured_language_codes()),
        }
    )
    return persist_language(request, response, language)


def language_context(request=None) -> dict:
    """Build template/API-friendly language metadata from Django settings."""
    current = resolve_language(request) if request is not None else normalize_language(getattr(settings, "LANGUAGE_CODE", "en")) or "en"
    default = normalize_language(getattr(settings, "LANGUAGE_CODE", "en")) or "en"
    bidi = set(getattr(settings, "LANGUAGES_BIDI", ("ar",)))
    languages = []
    for code, name in _language_pairs():
        try:
            from django.utils.translation import get_language_info

            info = get_language_info(code)
        except Exception:
            info = {}
        languages.append(
            {
                "code": code,
                "name": name,
                "name_local": info.get("name_local", name),
                "dir": "rtl" if code in bidi else "ltr",
                "is_current": code == current,
                "is_default": code == default,
            }
        )
    return {
        "languages": languages,
        "language": current,
        "default_language": default,
        "session_key": language_session_key(),
        "cookie_name": language_cookie_name(),
    }
