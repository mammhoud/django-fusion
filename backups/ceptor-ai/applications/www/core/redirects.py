"""Shared redirect helper for legacy slug aliases across the websites.

The class below was duplicated byte-for-byte in
``applications/ctc-research/www/urls.py`` and
``applications/lms-demo/www/urls.py`` so the consolidated helper lives
here. VResume does not use it because its slug-change redirects are
flat (no language prefix).
"""

from __future__ import annotations

from django.conf import settings
from django.views.generic.base import RedirectView


class LocalePreservingRedirectView(RedirectView):
    """RedirectView subclass that preserves the active i18n language prefix.

    A request to ``/de/about-page/`` activates the 'de' locale via
    ``i18n_patterns`` but would otherwise redirect to ``/about/``
    (default locale). This view prefixes the resolved target with the
    active language when it differs from the default.
    """

    permanent = True
    url: str | None = None

    def get_redirect_url(self, *args, **kwargs):  # type: ignore[override]
        redirect_url = super().get_redirect_url(*args, **kwargs)
        if not redirect_url:
            return redirect_url
        from django.utils.translation import get_language

        current_lang = get_language()
        default_lang = settings.LANGUAGE_CODE
        if current_lang and current_lang != default_lang and not redirect_url.startswith(f"/{current_lang}"):
            redirect_url = f"/{current_lang}{redirect_url}"
        return redirect_url
