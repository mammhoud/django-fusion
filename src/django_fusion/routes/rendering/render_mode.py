"""Canonical render-mode resolver for django-fusion and its products.

This module owns the single source of truth for answering "is this request
render-first (server HTML) or data-API (client JSON)?".

Before this module, the same priority chain was re-implemented in several
places with subtle drift (auto-seeding the session vs. only reading an
explicitly stored preference, different setting names, different fallback
defaults).  All of those paths now delegate here:

* ``FusionDualModeMixin.get_effective_render_first`` — component/fragment road.
* ``APISViewMixin.get_effective_render_first`` — the ``apis`` plugin road.
* precis-landing / precis / formint-pro / formint-client — the ``/apis/…``
  and ``/fusion/…`` render-mode reporting helpers.

Priority order (first match wins):

1. ``force_render_first`` — hard override to HTML mode.
2. ``force_data_mode`` — hard override to data mode.
3. ``X-Fusion-Render-First: true|false`` request header.
4. An **explicitly stored** session preference
   (``request.session["fusion_render_first"]``).  Deliberately *not* the
   auto-seeding ``get_session_render_first()`` heuristic: auto-seeding would
   override the configured default for plain browser traffic and make a
   ``FUSION_RENDER_FIRST=False`` deployment unreachable.
5. ``default`` (an explicit per-view/component override).
6. The Django setting (``FUSION_RENDER_FIRST``, with the legacy
   ``FUSION_RENDER_FIRST_DEFAULT`` / ``COMPONENTS_FUSION_RENDER_FIRST_DEFAULT``
   names still accepted), then ``setting_default``.
"""

from __future__ import annotations

from django.http import HttpRequest

from django_fusion.config.conf import (
    coerce_render_mode,
    resolve_render_first_setting,
    resolve_render_mode_setting,
)
from django_fusion.routes.rendering.session import SESSION_KEY

__all__ = [
    "header_render_first",
    "session_render_first",
    "resolve_render_first",
    "header_render_mode",
    "session_render_mode",
    "route_render_mode",
    "negotiate_mixed",
    "resolve_render_mode",
]


def header_render_first(request: HttpRequest | None) -> bool | None:
    """Return the per-request header override, or ``None`` when absent.

    Only the literal tokens ``true`` / ``false`` are honoured, so a stray or
    malformed header value can never silently flip the mode.
    """
    if request is None:
        return None
    try:
        header = request.headers.get("X-Fusion-Render-First")
    except Exception:  # noqa: BLE001 - header access is best-effort
        return None
    if header in ("true", "false"):
        return header == "true"
    return None


def session_render_first(request: HttpRequest | None) -> bool | None:
    """Return an explicitly stored session preference, or ``None``.

    Only a value the operator (or the settings UI) actually wrote into the
    session is consulted.  This intentionally avoids the auto-seeding
    heuristic in ``FusionSessionChecker`` so the configured setting default
    stays reachable for normal browser requests.
    """
    if request is None:
        return None
    try:
        if SESSION_KEY in request.session:
            return bool(request.session[SESSION_KEY])
    except Exception:  # noqa: BLE001 - no session middleware → no preference
        return None
    return None


def resolve_render_first(
    request: HttpRequest | None = None,
    *,
    force_render_first: bool | None = None,
    force_data_mode: bool = False,
    default: bool | None = None,
    setting_default: bool = False,
) -> bool:
    """Resolve the effective render-first preference for *request*.

    ``True`` → "fusion render first" (server HTML is the source of truth).
    ``False`` → "data APIs" (the client renders from JSON).

    See the module docstring for the full priority order.  ``default`` is an
    explicit per-view/component override; when ``None`` the Django setting is
    consulted, falling back to ``setting_default`` only when no setting name
    is configured at all.
    """
    if force_render_first:
        return True
    if force_data_mode:
        return False

    header = header_render_first(request)
    if header is not None:
        return header

    session_value = session_render_first(request)
    if session_value is not None:
        return session_value

    if default is not None:
        return bool(default)

    return resolve_render_first_setting(default=setting_default)


# ── String render-mode chain (FUSION_RENDER_MODE) ──────────────────────────
# Adds a third ``mixed`` mode to the render-first/data-API pair. ``mixed``
# negotiates per request: JSON clients (Accept: application/json) get data,
# everything else gets server HTML. A per-route override
# (FUSION_RENDER_MODE_ROUTES) lets specific paths pin a mode.

_MODE_HEADER = "X-Fusion-Render-Mode"
MODE_SESSION_KEY = "fusion_render_mode"


def header_render_mode(request: HttpRequest | None) -> str | None:
    """Return the per-request ``X-Fusion-Render-Mode`` override, or ``None``."""
    if request is None:
        return None
    try:
        header = request.headers.get(_MODE_HEADER)
    except Exception:  # noqa: BLE001
        return None
    return coerce_render_mode(header)


def session_render_mode(request: HttpRequest | None) -> str | None:
    """Return an explicitly stored session mode, or ``None``."""
    if request is None:
        return None
    try:
        if MODE_SESSION_KEY in request.session:
            return coerce_render_mode(request.session[MODE_SESSION_KEY])
    except Exception:  # noqa: BLE001
        return None
    return None


def route_render_mode(request: HttpRequest | None) -> str | None:
    """Resolve a per-route override from ``FUSION_RENDER_MODE_ROUTES``.

    The setting maps a path prefix to a mode (``{"/courses/": "mixed"}``).
    The longest matching prefix wins so more specific routes can override a
    broader one.
    """
    if request is None:
        return None
    try:
        from django.conf import settings

        routes = getattr(settings, "FUSION_RENDER_MODE_ROUTES", None)
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(routes, dict):
        return None
    path = getattr(request, "path", "")
    best: str | None = None
    best_len = -1
    for prefix, mode in routes.items():
        if not isinstance(prefix, str) or not path.startswith(prefix):
            continue
        coerced = coerce_render_mode(mode)
        if coerced is not None and len(prefix) > best_len:
            best = coerced
            best_len = len(prefix)
    return best


def negotiate_mixed(mode: str, request: HttpRequest | None) -> str:
    """Reduce a ``mixed`` mode to ``render`` or ``data`` for this request.

    API clients (``Accept: application/json``) receive ``data``; browsers and
    every other client receive ``render`` (full server HTML).
    """
    if mode != "mixed":
        return mode
    accept = ""
    if request is not None:
        try:
            accept = request.headers.get("Accept", "") or ""
        except Exception:  # noqa: BLE001
            accept = ""
    return "data" if "application/json" in accept.lower() else "render"


def resolve_render_mode(
    request: HttpRequest | None = None,
    *,
    force_render_first: bool | None = None,
    force_data_mode: bool = False,
    default: str | None = None,
    setting_default: str = "data",
    negotiate: bool = True,
) -> str:
    """Resolve the effective render mode for *request*.

    Returns ``render`` / ``data`` / ``mixed``. Priority order (first match):

    1. ``force_render_first`` / ``force_data_mode`` hard overrides.
    2. ``X-Fusion-Render-Mode: render|data|mixed`` request header.
    3. An explicitly stored session mode (``fusion_render_mode``).
    4. A per-route override (``FUSION_RENDER_MODE_ROUTES``).
    5. ``default`` (an explicit per-view/component override).
    6. The ``FUSION_RENDER_MODE`` setting (legacy bool names accepted).

    When ``negotiate`` is true (default), a resolved ``mixed`` is converted
    to a concrete ``render``/``data`` via Accept-header negotiation.
    """
    if force_render_first:
        return "render"
    if force_data_mode:
        return "data"

    mode = header_render_mode(request)
    if mode is None:
        mode = session_render_mode(request)
    if mode is None:
        mode = route_render_mode(request)
    if mode is None and default is not None:
        mode = coerce_render_mode(default)
    if mode is None:
        mode = resolve_render_mode_setting(default=setting_default)

    return negotiate_mixed(mode, request) if negotiate else mode
