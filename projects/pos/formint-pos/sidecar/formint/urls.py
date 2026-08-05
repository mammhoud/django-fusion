from django.urls import include, path

from django_fusion.contrib.api import branding, health, layouts

from . import views
from .api import api
from .handlers import FormintPageView
from .fusion import fusion_pointer_api

urlpatterns = [
    path('health/', views.health, name='formint-health'),
    # django_fusion.contrib.api — shared fusion API helpers (health/branding/layouts)
    path('fusion/health/', health, name='formint-fusion-health'),
    path('fusion/branding/', branding, name='formint-fusion-branding'),
    path('fusion/layouts/', layouts, name='formint-fusion-layouts'),
    # FusionCodec-encoded fragment pointer (session-aware; pairs with TS FusionDecoder)
    path('fusion/pointer/', fusion_pointer_api, name='formint-fusion-pointer'),
    # Session-mode settings toggle (FusionSessionChecker) — GET report / POST set / DELETE clear
    path('fusion/session-mode/', views.session_mode, name='formint-session-mode'),
    path('htmx/branches/summary/', views.branch_summary, name='formint-branch-summary'),
    path('htmx/tables/<str:resource>/', views.table_fragment, name='formint-table-fragment'),
    path('htmx/forms/<str:resource>/', views.form_fragment, name='formint-form-fragment'),
    path('fusion/branches/summary/', views.fusion_branch_summary, name='formint-fusion-branch-summary'),
    # Fusion render-mode contract (fragment-path mirror of /api/v1)
    path('fusion/render-mode/', views.render_mode, name='formint-render-mode'),
    path('fusion/navigation/', views.navigation, name='formint-navigation'),
    path('fusion/assets/', views.assets, name='formint-assets'),
    # Full-page render pipeline (django-fusion PageHandler) — HTMX vs full page
    path('fusion/page/', FormintPageView.as_view(), name='formint-page'),
    # Django Ninja + ninja-extra API (fusion encoder/decoder)
    path('api/v1/', api.urls),
]
