from django.urls import path

from . import api, views

urlpatterns = [
    path("auth/token/", api.token_api, name="token_api"),
    path("auth/refresh/", api.refresh_token_api, name="refresh_token_api"),
    path("auth/me/", api.current_user_api, name="current_user_api"),
    path("navigation/", views.navigation_api, name="navigation_api"),
    path("dashboard/", api.dashboard_api, name="dashboard_api"),
    path("workflows/", api.workflows_api, name="workflows_api"),
    path("integrations/", api.integrations_api, name="integrations_api"),
    path("custom-fields/", api.custom_fields_api, name="custom_fields_api"),
]
