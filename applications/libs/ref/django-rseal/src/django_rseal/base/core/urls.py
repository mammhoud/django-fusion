from __future__ import annotations

from django.urls import include, path
from django_grep.health.views import HealthCheckView

from django_rseal.apps import DjangoRsealConfig
from django_rseal.routes.newsletter.subscription import SubscribeView
from django_rseal.content.site import *
from django_rseal.content.site.auth.privacy import PrivacyModalView

app_name = DjangoRsealConfig.label

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/sign-in/", view=LoginView.as_view(), name="login"),
    path("auth/sign-up/", view=RegisterView.as_view(), name="register"),
    path("auth/sign-out/", view=LogoutView.as_view(), name="logout"),
    path(
        "auth/reset-password/", view=ResetPasswordView.as_view(), name="password_reset"
    ),  # getting by email
    path(
        "auth/forgot-password/", view=ForgotPasswordView.as_view(), name="password_forgot"
    ),  # search with email
    path("auth/verify-email/", view=VerifyEmailView.as_view(), name="verify-email-page"),  #
    path("auth/privacy/", view=PrivacyModalView.as_view(), name="privacy_modal"),
    path("notifications/", NotificationView.as_view(), name="notifications"),
    # Newsletter
    path("newsletter/subscribe/", SubscribeView.as_view(), name="subscribe_newsletter"),
    path("newsletter/", include("django_rseal.routes.newsletter.urls", namespace="newsletter")),
    # Chat bubble
    path("chat/", include("django_rseal.chat.urls", namespace="rseal_chat")),
]
