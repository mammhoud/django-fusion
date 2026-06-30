from __future__ import annotations

from django.urls import include, path
from django_grep.health.views import HealthCheckView

from ceptor_ai.apps import DjangoRsealConfig
from ceptor_ai.routes.newsletter.subscription import SubscribeView
from ceptor_ai.content.site import *
from ceptor_ai.content.site.auth.privacy import PrivacyModalView

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
    path("newsletter/", include("ceptor_ai.routes.newsletter.urls", namespace="newsletter")),
    # Chat bubble
    path("chat/", include("ceptor_ai.chat.urls", namespace="rseal_chat")),
]
