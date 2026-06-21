"""Root URL patterns for ctc-research — served from plugins/."""
from importlib.util import find_spec

from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.http import JsonResponse
from django.urls import include, path
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView


class EventListView(ListView):
    """Public event listing backed by the shared Event snippet model."""

    template_name = "events/events.html"
    context_object_name = "events"

    def get_queryset(self):
        from plugins.accounts.models import Event

        return Event.objects.filter(is_active=True, is_visible=True).order_by(
            "start_date", "title"
        )


class EventDetailView(DetailView):
    """Public event detail backed by the shared Event snippet model."""

    template_name = "events/detail.html"
    context_object_name = "event"

    def get_queryset(self):
        from plugins.accounts.models import Event

        return Event.objects.filter(is_active=True, is_visible=True)


class NewsletterSubscribeView(View):
    """Simple newsletter subscription stub."""

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."}, status=400)
        return JsonResponse({"status": "ok", "message": "Thank you for subscribing!"})


app_name = "plugins"

urlpatterns = [
    path("events/", EventListView.as_view(), name="events"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    # accounts plugin — explicit namespace so {% url 'accounts:...' %} resolves
    path("accounts/", include("plugins.accounts.urls", namespace="accounts")),
    path("profile/", include("plugins.profile.urls", namespace="profile")),
    # LMS plugin (courses, learning, enrollments)
    path("learning/", include("plugins.lms.urls", namespace="lms")),
    # Auth URL aliases
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", SignupView.as_view(), name="register"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    path(
        "auth/privacy-modal/",
        TemplateView.as_view(template_name="auth/privacy_modal_content.html"),
        name="privacy_modal",
    ),
    path(
        "auth/newsletter/subscribe/",
        NewsletterSubscribeView.as_view(),
        name="subscribe_newsletter",
    ),
]

# Products plugin — optional, guard so missing module doesn't break URL loading
if find_spec("plugins.products") is not None and find_spec("plugins.products.urls") is not None:
    urlpatterns.append(path("", include("plugins.products.urls", namespace="products")))
