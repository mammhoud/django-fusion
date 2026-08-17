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

from django_fusion.config.conf import resolve_render_first_setting
from django_fusion.routes.rendering.session import SESSION_KEY

__all__ = [
    "header_render_first",
    "session_render_first",
    "resolve_render_first",
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
