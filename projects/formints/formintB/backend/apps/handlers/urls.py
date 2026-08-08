"""POS Cloud — Handlers URL routing (django-fusion API-first surface)."""

from django.urls import path

from apps.handlers.fusion import (
    assets, fusion_health, navigation, render_mode, session_mode,
)

urlpatterns = [
    # Fusion contract — served at /fusion/* (sidecar-compatible)
    path("health", fusion_health, name="fusion_health"),
    path("render-mode", render_mode, name="fusion_render_mode"),
    path("nav", navigation, name="fusion_nav"),
    path("session-mode", session_mode, name="fusion_session_mode"),
    path("assets", assets, name="fusion_assets"),
]
