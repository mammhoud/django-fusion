from django.urls import path

from . import api, views

urlpatterns = [
    path("auth/token/", api.token_api, name="token_api"),
    path("auth/refresh/", api.refresh_token_api, name="refresh_token_api"),
    path("auth/me/", api.current_user_api, name="current_user_api"),
    path("navigation/", views.navigation_api, name="navigation_api"),
    path("dashboard/", api.dashboard_api, name="dashboard_api"),
    path("workspace/current/", api.workspace_current_api, name="workspace_current_api"),
    path("workflows/", api.workflows_api, name="workflows_api"),
    path("integrations/", api.integrations_api, name="integrations_api"),
    path("custom-fields/", api.custom_fields_api, name="custom_fields_api"),
    path("custom-objects/", api.custom_objects_api, name="custom_objects_api"),
    path("custom-objects/<str:key>/records/", api.custom_object_records_api, name="custom_object_records_api"),
    path(
        "custom-objects/<str:key>/records/<int:pk>/",
        api.custom_object_record_detail_api,
        name="custom_object_record_detail_api",
    ),
    path("saved-views/", api.saved_views_api, name="saved_views_api"),
    path("saved-views/<int:pk>/", api.saved_view_detail_api, name="saved_view_detail_api"),
    path("webhooks/", api.resource_api, {"resource": "webhooks"}, name="webhooks_api"),
    path("email/accounts/", api.email_accounts_api, name="email_accounts_api"),
    path("email/accounts/<int:pk>/sync/", api.email_account_sync_api, name="email_account_sync_api"),
    path("email/messages/", api.email_messages_api, name="email_messages_api"),
    path("export/", api.resource_export, name="resource_export"),
]
