"""Content-calendar pages and HTMX interactions."""
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.views import LoopPageView

from .forms import PostComposerForm, PostLifecycleForm
from .models import Post, SocialChannel


def post_rows() -> list[Post]:
    try:
        return list(
            Post.objects.select_related("workspace", "campaign", "channel")
            .order_by("-scheduled_at")[:50]
        )
    except (OperationalError, ProgrammingError):
        return []


class ContentCalendarView(LoopPageView):
    """Postiz-style content calendar using persisted posts only."""

    template_name = "dashboard/content_calendar.html"
    module_id = "marketing"
    page_title = "Content calendar"
    page_kicker = "Marketing · calendar"
    page_description = "Compose, review, schedule, and publish content without hiding its lifecycle."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            workspace_id = self.request.user.profile.workspace_id
        except Exception:  # noqa: BLE001 - a profile is optional for auth
            workspace_id = None
        channels = SocialChannel.objects.filter(workspace_id=workspace_id) if workspace_id else SocialChannel.objects.none()
        for channel in channels:
            if not channel.oauth_token:
                channel.status = "disconnected"
            elif channel.token_expires_at and channel.token_expires_at <= timezone.now():
                channel.status = "expired"
            else:
                channel.status = "connected"
        context.update(
            {
                "posts": post_rows(),
                "post_form": PostComposerForm(),
                "channels": channels,
                "linkedin_configured": bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET),
                "x_configured": bool(settings.X_CLIENT_ID and settings.X_CLIENT_SECRET),
            }
        )
        return context


def _post_fragment_context() -> dict:
    return {"posts": post_rows(), "post_form": PostComposerForm()}


@require_POST
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostComposerForm(request.POST)
    if not form.is_valid():
        return render(request, "dashboard/partials/post_form.html", {"post_form": form}, status=422)
    post = form.save(commit=False)
    if getattr(request.user, "is_authenticated", False):
        post.created_by = request.user
    post.save()
    return render(request, "dashboard/partials/post_success.html", _post_fragment_context())


@require_POST
def post_transition(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    form = PostLifecycleForm(request.POST)
    if not form.is_valid():
        return render(request, "dashboard/partials/post_row.html", {"post": post}, status=422)

    action = form.cleaned_data["action"]
    target = {
        "submit": "pending_approval",
        "approve": "approved",
        "schedule": "scheduled",
        "publish": "publishing",
        "reset": "draft",
    }[action]
    try:
        post.transition_to(target)
    except ValidationError:
        return render(
            request,
            "dashboard/partials/post_row.html",
            {"post": post, "post_error": f"Cannot {action} a {post.get_status_display()} post."},
            status=409,
        )

    if action == "publish":
        try:
            from plugins.workers.tasks import publish_post

            publish_post.send(post.pk)
        except Exception as exc:  # noqa: BLE001 - record a real queue failure
            post.status = "failed"
            post.save(update_fields=["status", "updated_at"])
            post_error = f"Publishing queue unavailable: {exc.__class__.__name__}"
        else:
            post_error = ""
    else:
        post_error = ""
    return render(request, "dashboard/partials/post_row.html", {"post": post, "post_error": post_error})
