"""Assets endpoint for django-fusion components.

Provides API endpoints that return the CSS, font, and JS assets that
components need for rendering. Used by Next.js frontends to dynamically
load top assets (in ``<head>``) and bottom assets (before ``</body>``).

Usage — add to root URLs::

    from django_fusion.core.assets import urls as assets_urls
    urlpatterns += [path("fusion/assets/", include(assets_urls))]

The endpoints are:

* ``GET /fusion/assets/top/`` — CSS links, font preloads, meta for ``<head>``
* ``GET /fusion/assets/bottom/`` — JS scripts for ``</body>``
* ``GET /fusion/assets/manifest/`` — full manifest (top + bottom)

Configurable via ``FUSION_ASSETS`` Django setting::

    FUSION_ASSETS = {
        "top": {
            "css": ["/static/css/fusion.css"],
            "fonts": ["/static/fonts/inter/styles.css"],
            "preconnect": ["https://fonts.googleapis.com"],
        },
        "bottom": {
            "js": ["/static/js/fusion-bridge.js"],
        },
    }
"""

from .views import (  # noqa: F401
    AssetsBottomView,
    AssetsManifestView,
    AssetsTopView,
)
