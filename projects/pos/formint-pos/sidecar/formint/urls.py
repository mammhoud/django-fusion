from django.urls import include, path

from . import views
from .api import api

urlpatterns = [
    path('health/', views.health, name='formint-health'),
    path('htmx/branches/summary/', views.branch_summary, name='formint-branch-summary'),
    path('htmx/tables/<str:resource>/', views.table_fragment, name='formint-table-fragment'),
    path('htmx/forms/<str:resource>/', views.form_fragment, name='formint-form-fragment'),
    path('fusion/branches/summary/', views.fusion_branch_summary, name='formint-fusion-branch-summary'),
    # Fusion render-mode contract (fragment-path mirror of /api/v1)
    path('fusion/render-mode/', views.render_mode, name='formint-render-mode'),
    path('fusion/navigation/', views.navigation, name='formint-navigation'),
    path('fusion/assets/', views.assets, name='formint-assets'),
    # Django Ninja + ninja-extra API (fusion encoder/decoder)
    path('api/v1/', api.urls),
]
