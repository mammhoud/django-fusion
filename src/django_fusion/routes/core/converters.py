"""
URL path converters for Django URL routing.

Provides ``UnicodeSlugConverter`` — a drop-in replacement for Django's
built-in ``slug`` converter that accepts Unicode word characters
(including Arabic, Cyrillic, CJK, etc.) plus ASCII hyphens.

Usage::

    from django.urls import path, register_converter
    from django_fusion.routes.core.converters import UnicodeSlugConverter

    register_converter(UnicodeSlugConverter, "unislug")

    urlpatterns = [
        path("pages/<unislug:slug>/", view),
    ]
"""


class UnicodeSlugConverter:
    """
    Slug converter that accepts Unicode word characters (including Arabic,
    Cyrillic, CJK, etc.) plus ASCII hyphens, rejecting spaces, slashes,
    and other special characters.

    Uses Python 3's Unicode-aware ``\\w`` (from the ``re`` module), which in
    Python 3 matches word characters from **any** Unicode script when used
    with a :class:`str` pattern.

    Usage in URL patterns::

        from django.urls import path, register_converter
        from django_fusion.routes.core.converters import UnicodeSlugConverter

        register_converter(UnicodeSlugConverter, "unislug")

        urlpatterns = [
            path("pages/<unislug:slug>/", view),
        ]

    This is a drop-in replacement for Django's built-in ``slug`` converter
    which only accepts ``[-a-zA-Z0-9_]+`` and rejects non-ASCII scripts.
    """

    regex = r"[-\w]+"

    def to_python(self, value: str) -> str:
        return value

    def to_url(self, value: str) -> str:
        return value
