"""
Formint — UserSettings → Fusion session render-mode sync.

Bridge between the operator-facing Unfold admin settings page
(``UserSettings.fusion_render_mode``) and the per-session render-mode
preference consumed by ``django_fusion.routes.rendering.session``
(``FusionSessionChecker`` / ``get_effective_render_first``).

Flow
----
1. ``FormintSessionModeMiddleware`` — on the first request of each session
   (flag not yet set), reads the authenticated user's ``UserSettings`` row
   and pushes ``fusion_render_mode`` into the session so
   ``get_effective_render_first()`` honours the stored admin preference
   without a per-request DB query afterwards.
2. ``UserSettingsAdmin.save_model`` — when an operator saves the settings
   page, ``apply_user_settings_to_session`` is called directly so the
   change takes effect on their very next request.

Mapping
-------
* ``fusion``  → ``FusionSessionChecker.set_preference(request, True)``
  (server-rendered HTML first)
* ``data``    → ``FusionSessionChecker.set_preference(request, False)``
  (JSON APIs)
* ``default`` → ``FusionSessionChecker.clear_preference(request)`` so the
  configured ``FUSION_RENDER_FIRST_DEFAULT`` applies.
"""

from __future__ import annotations

from django.http import HttpRequest

from django_fusion.routes.rendering.session import session_checker

from formint.models import UserSettings

__all__ = [
    "FormintSessionModeMiddleware",
    "apply_user_settings_to_session",
    "seed_user_settings_session",
]


def apply_user_settings_to_session(
    request: HttpRequest,
    mode: str | None = None,
) -> None:
    """Push the authenticated user's ``UserSettings`` mode into the session.

    By default reads the operator's own settings row (the row whose ``user``
    FK points at ``request.user``) and applies its ``fusion_render_mode``
    via ``FusionSessionChecker``. Callers that already hold the row (e.g.
    ``UserSettingsAdmin.save_model``) can pass ``mode`` directly to skip
    the DB read. No-op for anonymous users / missing rows.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return

    if mode is None:
        settings_obj = UserSettings.objects.filter(user=user).first()
        if settings_obj is None:
            return
        mode = settings_obj.fusion_render_mode
    if mode == "fusion":
        session_checker.set_preference(request, True)
    elif mode == "data":
        session_checker.set_preference(request, False)
    else:  # "default" — clear any explicit value so the settings default applies
        session_checker.clear_preference(request)


class FormintSessionModeMiddleware:
    """Seed the session render-mode preference from the operator's settings.

    Runs before every response. On the first request of a session it reads
    the authenticated user's ``UserSettings.fusion_render_mode`` and writes
    the matching session preference; the ``_fusion_settings_synced`` flag
    prevents repeated DB lookups on subsequent requests. The admin
    ``save_model`` path re-applies immediately (see formint/admin.py).

    Note: the one-time query also runs for the first request of any
    authenticated session, including token/device API sessions (cheap — a
    single indexed ``UserSettings`` lookup, once per session).
    """

    SYNCED_KEY = "_fusion_settings_synced"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        self._seed_session(request)
        return self.get_response(request)

    def _seed_session(self, request: HttpRequest) -> None:
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return
        session = getattr(request, "session", None)
        if session is None or session.get(self.SYNCED_KEY):
            return
        seed_user_settings_session(request)

    @classmethod
    def mark_synced(cls, request: HttpRequest) -> None:
        """Record that this session has been seeded from UserSettings."""
        session = getattr(request, "session", None)
        if session is not None:
            session[cls.SYNCED_KEY] = True


def seed_user_settings_session(
    request: HttpRequest,
    mode: str | None = None,
) -> None:
    """Apply the user settings preference and mark the session as synced.

    Convenience used by the middleware (first request per session) and by
    ``UserSettingsAdmin.save_model`` (immediate re-seed after an admin save,
    passing the just-saved ``mode`` to avoid a second DB query).
    """
    apply_user_settings_to_session(request, mode=mode)
    FormintSessionModeMiddleware.mark_synced(request)
