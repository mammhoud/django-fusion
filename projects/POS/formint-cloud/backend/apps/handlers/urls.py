"""POS Cloud — Handlers URL routing (django-fusion API-first surface)."""

from django.urls import path

from apps.handlers.fusion import (
    assets, fusion_health, navigation, render_mode, session_mode,
)
from apps.handlers.surface import fusion_monitor

urlpatterns = [
    # Fusion contract — served at /fusion/* (server-compatible)
    path("health", fusion_health, name="fusion_health"),
    path("render-mode", render_mode, name="fusion_render_mode"),
    path("nav", navigation, name="fusion_nav"),
    path("session-mode", session_mode, name="fusion_session_mode"),
    path("assets", assets, name="fusion_assets"),
    # Monitor tile — rendered fragment (last backup + sync queue depth)
    path("monitor", fusion_monitor, name="fusion_monitor"),
]
