"""Template language context built from the active Django settings."""

from django_fusion.core.middlewares.language import language_context


def LANGUAGES(request=None):
    """Return language metadata for Django, Wagtail, HTMX, and Astro bridges.

    The consuming site remains responsible for its admin-editable Wagtail
    ``SiteLanguage`` rows; this context is the settings-level base catalog and
    never invents a second language list.
    """
    return language_context(request)
