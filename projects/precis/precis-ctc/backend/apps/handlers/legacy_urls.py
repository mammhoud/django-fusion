"""
Legacy `handlers` namespace — reverse-compatibility URLconf.

The pre-merge LMS mounted the profile, cart/checkout and accounts surfaces under
a single `handlers` namespace. Templates and views still reverse names like
``handlers:settings``, ``handlers:cart-count``, and ``handlers:checkout`` (see
the profile nav-menu, settings forms, cart drawer, and component partials).

The routes themselves are owned by the ``profile`` (``apps.pages.profile``) and
``cart`` (``apps.core``) app namespaces, which are included earlier in
``apps/urls.py`` and therefore still win URL resolution. This module exists only
so that ``{% url 'handlers:…' %}`` and ``reverse("handlers:…")`` resolve.

The sub-patterns are imported as *lists*, not via module include, so their own
``app_name`` attributes do not nest the namespace: every name is registered
directly under ``handlers`` (e.g. ``handlers:settings``, ``handlers:cart-count``).
"""

from django.urls import include, path

from apps.core import urls as cart_urls
from apps.pages.profile import urls as profile_urls

app_name = "handlers"

urlpatterns = [
    # Profile surfaces (dashboard, settings, messages, certifications, blog
    # management, …) — canonical URLconf patterns, re-mapped under the legacy
    # namespace. Path prefixes match the canonical mounts in apps/pages/urls.py.
    path("profile/", include(profile_urls.urlpatterns)),
    # Cart & checkout endpoints — same URLconf patterns so `handlers:cart-count`
    # / `handlers:checkout` resolve to the canonical /cart/ routes.
    path("cart/", include(cart_urls.urlpatterns)),
]
