"""
Pages plugin — shared static page content definitions for LMS Fusion.

Provides ``STATIC_PAGES``, a dict of all static public page content that is
consumed by both the Django API views and the django-fusion fragment
rendering system.

Import this module in API views instead of duplicating the data::

    from apps.pages.pages.content import STATIC_PAGES, normalize_slug
"""
