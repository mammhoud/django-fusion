"""
Shared static page content definitions for Fusion CMS.

Moved from ``www.api.pages`` to a reusable plugin module so that both the
API views and the django-fusion fragment components can import the same
canonical page data without circular imports.
"""


def cta(label, href, variant="primary"):
    return {"label": label, "href": href, "variant": variant}


STATIC_PAGES: dict[str, dict] = {}
# STATIC_PAGES has been emptied. All page content now comes from Wagtail
# fixture data loaded via loaddata. See assets/fixtures/dump-data.json for
# the page tree. The normalize_slug() helper below is kept for backward
# compatibility in the API layer.


def normalize_slug(slug: str) -> str:
    """Normalize a URL slug to the keys used in ``STATIC_PAGES``."""
    return "home" if slug in ("", "home", "index") else slug.strip("/")
