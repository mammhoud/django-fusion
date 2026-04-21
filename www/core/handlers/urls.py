# type: ignore NOQA
# from __future__ import annotations

from allauth.account.decorators import secure_admin_login
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic.base import TemplateView

from .apps import AccountsConfig
from .site import *

app_name = AccountsConfig.label


urlpatterns = [
    path("profile/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("profile/profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("profile/courses/", CoursesView.as_view(), name="courses"),
    path("profile/Certificates/", CertificationsView.as_view(), name="certifications"),
    path("profile/notes/", NotesView.as_view(), name="notes"),
    path("profile/settings/", SettingsView.as_view(), name="settings"),
    path("profile/messages/", MessagesView.as_view(), name="messages"),
    # Blog post management
    path("profile/blog/", BlogPostsView.as_view(), name="blog-posts"),
    path("profile/blog/create/", BlogPostCreateView.as_view(), name="blog-post-create"),
    path("profile/blog/<int:post_id>/edit/", BlogPostEditView.as_view(), name="blog-post-edit"),
    path("profile/blog/<int:post_id>/delete/", BlogPostDeleteView.as_view(), name="blog-post-delete"),
] + [  # Action endpoints
    path("profile/update/", ProfileView.as_view(), name="profile-update"),
    path("profile/image/upload/", ProfileImageUploadView.as_view(), name="profile-image-upload"),
    path("profile/image/update/", ProfileImageUploadView.as_view(), name="profile-update-image"),
    path("profile/image/remove/", ProfileImageRemoveView.as_view(), name="profile-remove-image"),
    path(
        "profile/notifications/update/", ProfileView.as_view(), name="profile-notifications-update"
    ),
    path("profile/security/update/", ProfileView.as_view(), name="profile-security-update"),
    path("profile/settings/change-password/", ProfileView.as_view(), name="change_password"),
    path(
        "profile/settings/cancel-subscription/", ProfileView.as_view(), name="cancel_subscription"
    ),
    path("profile/settings/update-plan/", ProfileView.as_view(), name="update_plan"),
    path("profile/settings/delete-account/", ProfileView.as_view(), name="delete_account"),
    path("profile/settings/export-data/", ProfileView.as_view(), name="export_data"),
    path("profile/settings/revoke-sessions/", ProfileView.as_view(), name="revoke_sessions"),
    path("profile/settings/verify-2fa/", ProfileView.as_view(), name="verify_2fa"),
    path("profile/settings/disable-2fa/", ProfileView.as_view(), name="disable_2fa"),
    path("profile/settings/enable-2fa/", ProfileView.as_view(), name="enable_2fa"),
] + [  # Cart endpoints
    path("cart/count/", CartCountView.as_view(), name="cart-count"),
    path("cart/items/", CartView.as_view(), name="cart-items"),
    path("cart/subtotal/", CartSubtotalView.as_view(), name="cart-subtotal"),
    path("cart/update/<str:item_id>/", CartUpdateQuantityView.as_view(), name="cart-update-quantity"),
    path("cart/remove/<str:item_id>/", CartRemoveItemView.as_view(), name="cart-remove-item"),
    path("cart/add/", CartAddItemView.as_view(), name="cart-add-item"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
] + [  # Registration endpoints
    path("", include("apps.accounts.registration.urls")),
]

