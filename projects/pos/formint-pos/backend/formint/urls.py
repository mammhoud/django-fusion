from django.urls import include, path

from . import views
from .api import api

urlpatterns = [
    path('health/', views.health, name='formint-health'),
    path('htmx/branches/summary/', views.branch_summary, name='formint-branch-summary'),
    path('htmx/tables/<str:resource>/', views.table_fragment, name='formint-table-fragment'),
    path('htmx/forms/<str:resource>/', views.form_fragment, name='formint-form-fragment'),
    path('fusion/branches/summary/', views.fusion_branch_summary, name='formint-fusion-branch-summary'),
    # Django Ninja + ninja-extra API (fusion encoder/decoder)
    path('api/v1/', api.urls),
]
