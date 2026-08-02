"""
Fusion CMS — Routable Components Site Configuration
======================================================

Assembles the Application and Site hierarchy for the routable-components
routing system. Each Application (with its own ``viewsets`` property)
lives in its related app directory; core only wires them into the Site.

All fragment components are registered in their related app's Application
viewsets — there is no separate ``HTMXApplication`` / ``/actions/`` prefix.

  LMSApp      → apps/pages/lms/application.py
  BlogApp     → apps/pages/blog/application.py
  AccountsApp → apps/pages/accounts/application.py
  EventsApp   → apps/pages/events/application.py
  CoreApp     → apps/core/application.py

Wired into www/urls.py::

    from apps.core.routes import site
    urlpatterns += [site.url_pattern]

Generated URL prefix: / (root)
  /lms/dashboard/
  /lms/courses/grid/                (HTMX action fragment)
  /lms/courses/filters/             (HTMX action fragment)
  /lms/dashboard/kpis/              (HTMX action fragment)
  /blog/posts/                       (HTMX action fragment)
  /blog/posts/list-fragment/
  /blog/posts/create-fragment/
  /events/                       → list
  /events/event/                 → list
  /events/event/<pk>/detail/     → detail
  /events/list-fragment/         (HTMX action fragment)
  /events/create-fragment/       (HTMX action fragment, staff only)
  /core/cms/head-content/           (HTMX action fragment)
  /core/checkout/                   (HTMX action fragment)
"""

from __future__ import annotations

from django_fusion.routes.core.sites import Site

from apps.core.application import CoreApp
from apps.pages.accounts.application import AccountsApp
from apps.pages.blog.application import BlogApp
from apps.pages.events.application import EventsApp
from apps.pages.lms.application import LMSApp

# -----------------------------------------------------------------------
# Site assembly
# -----------------------------------------------------------------------


class FusionSite(Site):
    """Root Site for Fusion CMS.

    ``Site`` inherits ``IndexViewMixin``, whose ``index_path`` registers a
    ``path("", _IndexRedirectView...)`` that 302-redirects the root URL to the
    first suitable viewset URL.  The routable component Site is mounted at
    the URL root (``""`` in www/urls.py), so that auto-redirect would hijack
    ``/`` and shadow the Wagtail homepage.  Setting ``index_path = None``
    removes the inherited pattern (the ``ViewsetMeta`` metaclass treats a
    ``None`` value as "remove inherited pattern") so Wagtail keeps serving ``/``
    while ``/lms/...`` and ``/blog/...`` live at the root.
    """

    index_path = None


_site = None


def get_site() -> FusionSite:
    """Build the Site once, memoized at module import.

    The Site instance is created when ``www/urls.py`` imports ``site`` from
    this module — after Django has fully initialized the app registry.
    Applications are imported at the top of this module, so their ``viewsets``
    lazy-import components/viewsets only when first accessed.

    Fragment components are registered in their related app's Application
    viewsets, not in a separate ``HTMXApplication``.  The unified Site
    routing tree serves all app routes and action fragments under their
    app prefix (e.g. ``/lms/courses/grid/``, ``/blog/posts/``).

    Events are now served from ``apps.pages.events.application.EventsApp``
    under the ``events`` namespace (``/events/``), not ``accounts``.
    """
    global _site
    if _site is None:
        _site = FusionSite(
            title="Fusion CMS",
            viewsets=[
                LMSApp(),
                BlogApp(),
                AccountsApp(),
                EventsApp(),
                CoreApp(),
            ],
        )
    return _site


# Backwards-compatible import target for www/urls.py — use the lazy version.
site = get_site()