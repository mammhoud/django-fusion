"""Content-calendar pages and HTMX interactions."""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.tenancy import current_workspace_id
from apps.core.views import LoopPageView

from .forms import PostComposerForm, PostLifecycleForm
from .models import Post, SocialChannel


def _channel_status(channel: SocialChannel) -> str:
    """Derive a render-safe connection status for a channel."""
    if not channel.oauth_token:
        return "disconnected"
    if channel.token_expires_at and channel.token_expires_at <= timezone.now():
        return "expired"
    return "connected"


def channel_rows(request: HttpRequest) -> list[SocialChannel]:
    workspace_id = current_workspace_id(request)
    queryset = SocialChannel.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        channels = list(queryset.order_by("platform", "account_name"))
    except (OperationalError, ProgrammingError):
        channels = []
    for channel in channels:
        channel.status = _channel_status(channel)
    return channels


def post_rows(request: HttpRequest) -> list[Post]:
    workspace_id = current_workspace_id(request)
    queryset = Post.objects.select_related("workspace", "campaign", "channel")
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        return list(queryset.order_by("-scheduled_at")[:50])
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
        context.update(
            {
                "posts": post_rows(self.request),
                "post_form": PostComposerForm(request=self.request),
                "channels": channel_rows(self.request),
                "linkedin_configured": bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET),
                "x_configured": bool(settings.X_CLIENT_ID and settings.X_CLIENT_SECRET),
            }
        )
        return context


class ChannelListView(LoopPageView):
    """Manage connected social accounts: connect, disconnect, refresh."""

    template_name = "dashboard/channels.html"
    module_id = "marketing"
    page_title = "Channels"
    page_kicker = "Marketing · channels"
    page_description = "Connect provider accounts and see their publish and analytics capabilities."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "channels": channel_rows(self.request),
                "linkedin_configured": bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET),
                "x_configured": bool(settings.X_CLIENT_ID and settings.X_CLIENT_SECRET),
            }
        )
        return context


def _channel_fragment_context(request: HttpRequest) -> dict:
    return {"channels": channel_rows(request)}


@require_POST
@login_required
def channel_disconnect(request: HttpRequest, pk: int) -> HttpResponse:
    """Soft-disconnect a channel (never delete its published posts)."""
    workspace_id = current_workspace_id(request)
    queryset = SocialChannel.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    channel = get_object_or_404(queryset, pk=pk)
    channel.is_active = False
    channel.oauth_token = ""
    channel.oauth_refresh_token = ""
    channel.token_expires_at = None
    channel.save(update_fields=["is_active", "oauth_token", "oauth_refresh_token", "token_expires_at", "updated_at"])
    return render(request, "dashboard/partials/channel_list.html", _channel_fragment_context(request))


@require_POST
@login_required
def channel_refresh(request: HttpRequest, pk: int) -> HttpResponse:
    """Queue an OAuth token refresh for a connected channel."""
    workspace_id = current_workspace_id(request)
    queryset = SocialChannel.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    channel = get_object_or_404(queryset, pk=pk)
    try:
        from plugins.workers.tasks import refresh_oauth_token

        refresh_oauth_token.send(channel.pk)
        refreshed = True
    except Exception as exc:  # noqa: BLE001 - record a real queue failure
        refreshed = False
        channel.refresh_error = f"Refresh queue unavailable: {exc.__class__.__name__}"
    else:
        channel.refresh_error = ""
    context = _channel_fragment_context(request)
    context["refreshed"] = refreshed
    return render(request, "dashboard/partials/channel_list.html", context)


def _post_fragment_context(request: HttpRequest) -> dict:
    return {"posts": post_rows(request), "post_form": PostComposerForm(request=request)}


@require_POST
@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostComposerForm(request.POST, request=request)
    if not form.is_valid():
        return render(request, "dashboard/partials/post_form.html", {"post_form": form}, status=422)
    post = form.save(commit=False)
    workspace_id = current_workspace_id(request)
    if workspace_id is not None:
        post.workspace_id = workspace_id
    if getattr(request.user, "is_authenticated", False):
        post.created_by = request.user
    post.save()
    return render(request, "dashboard/partials/post_success.html", _post_fragment_context(request))


@require_POST
@login_required
def post_transition(request: HttpRequest, pk: int) -> HttpResponse:
    workspace_id = current_workspace_id(request)
    queryset = Post.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    post = get_object_or_404(queryset, pk=pk)
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
