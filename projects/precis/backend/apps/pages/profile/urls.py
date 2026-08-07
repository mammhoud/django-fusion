# type: ignore NOQA

from django.urls import path

from .apps import ProfileConfig
from .views import (
    CertificationsView,
    CoursesView,
    DashboardView,
    MessagesView,
    NotesView,
    ProfileEditView,
    ProfileImageRemoveView,
    ProfileImageUploadView,
    ProfileView,
    SettingsView,
)

# Blog views are optional — only available when apps.pages.blog is in INSTALLED_APPS
try:
    from .views import (
        BlogPostCreateView,
        BlogPostDeleteView,
        BlogPostEditView,
        BlogPostsView,
    )
    _blog_urls_available = (
        BlogPostsView is not None and
        BlogPostCreateView is not None and
        BlogPostEditView is not None and
        BlogPostDeleteView is not None
    )
except (ImportError, TypeError):
    _blog_urls_available = False

app_name = ProfileConfig.label


urlpatterns = [
    # Main profile pages
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("courses/", CoursesView.as_view(), name="courses"),
    path("certifications/", CertificationsView.as_view(), name="certifications"),
    path("notes/", NotesView.as_view(), name="notes"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("messages/", MessagesView.as_view(), name="messages"),
] + ([
    # Blog post management — only when blog views are available
    path("blog/", BlogPostsView.as_view(), name="blog-posts"),
    path("blog/create/", BlogPostCreateView.as_view(), name="blog-post-create"),
    path("blog/<int:post_id>/edit/", BlogPostEditView.as_view(), name="blog-post-edit"),
    path("blog/<int:post_id>/delete/", BlogPostDeleteView.as_view(), name="blog-post-delete"),
] if _blog_urls_available else []) + [
    # Action endpoints
    path("update/", ProfileView.as_view(), name="profile-update"),
    path("image/upload/", ProfileImageUploadView.as_view(), name="profile-image-upload"),
    path("image/update/", ProfileImageUploadView.as_view(), name="profile-update-image"),
    path("image/remove/", ProfileImageRemoveView.as_view(), name="profile-remove-image"),
    path("notifications/update/", ProfileView.as_view(), name="profile-notifications-update"),
    path("security/update/", ProfileView.as_view(), name="profile-security-update"),
    path("settings/change-password/", ProfileView.as_view(), name="change_password"),
    path("settings/cancel-subscription/", ProfileView.as_view(), name="cancel_subscription"),
    path("settings/update-plan/", ProfileView.as_view(), name="update_plan"),
    path("settings/delete-account/", ProfileView.as_view(), name="delete_account"),
    path("settings/export-data/", ProfileView.as_view(), name="export_data"),
    path("settings/revoke-sessions/", ProfileView.as_view(), name="revoke_sessions"),
    path("settings/verify-2fa/", ProfileView.as_view(), name="verify_2fa"),
    path("settings/disable-2fa/", ProfileView.as_view(), name="disable_2fa"),
    path("settings/enable-2fa/", ProfileView.as_view(), name="enable_2fa"),
]
