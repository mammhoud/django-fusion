"""Language middleware for django-fusion projects.

``DefaultLanguageMiddleware`` ensures a ``language`` cookie is always
set so that Django's ``LocaleMiddleware`` can pick up the user's
preference across requests.

In addition to the cookie, the middleware honours a ``?lang=`` query
parameter so that client-side language switchers (e.g. single-page
apps) can change the language without a full server round-trip.
"""

from django.conf import settings
from django.utils.translation import activate


class DefaultLanguageMiddleware:
    """Activate the correct language and persist it via a cookie.

    Priority:
    1. ``?lang=`` query parameter — explicit user choice (highest)
    2. ``language`` cookie — persisted preference
    3. ``settings.LANGUAGE_CODE`` — project default
    """

    cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        requested_lang = request.GET.get("lang")
        cookie_lang = request.COOKIES.get(self.cookie_name)
        default_lang = settings.LANGUAGE_CODE

        # Resolve the active language — explicit ``?lang=`` wins over
        # cookie, which wins over the project default.
        active_lang = requested_lang or cookie_lang or default_lang

        # Only accept known languages to avoid spurious codes
        known_codes = {code for code, _name in settings.LANGUAGES}
        if active_lang not in known_codes:
            active_lang = default_lang

        activate(active_lang)

        response = self.get_response(request)

        # Persist the choice: always set (or refresh) the cookie so the
        # next request without ``?lang=`` still gets the right language.
        if requested_lang or self.cookie_name not in request.COOKIES:
            response.set_cookie(
                self.cookie_name,
                active_lang,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )

        return response
