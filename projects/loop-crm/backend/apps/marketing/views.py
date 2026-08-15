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

from apps.core.realtime import safe_publish_workspace_event
from apps.core.tenancy import current_workspace_id
from apps.core.views import LoopPageView

from .connector_adapters import MANUAL_CONNECT
from .connectors import platform_catalog
from .forms import ChannelConnectForm, PostComposerForm, PostLifecycleForm
from .models import Media, Post, SocialChannel


class ApprovalsView(LoopPageView):
    """Approval queue — posts awaiting review before they can be scheduled."""

    template_name = "dashboard/approvals.html"
    module_id = "marketing"
    page_title = "Approvals"
    page_kicker = "Marketing · review"
    page_description = "Posts waiting for approval. Approve to move them to the schedule, or send them back to draft."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        queryset = Post.objects.filter(status="pending_approval").select_related("channel", "campaign")
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        context["pending_posts"] = list(queryset.order_by("scheduled_at"))
        return context


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


class MediaListView(LoopPageView):
    """Media library — a real, workspace-scoped list of uploaded assets.

    Media upload is a file (multipart) concern, so it is intentionally not a
    JSON resource in ``apps.core.resources``; this screen only lists what has
    already been uploaded and attachable to posts.
    """

    template_name = "dashboard/resource_list.html"
    module_id = "marketing"
    page_title = "Media library"
    page_kicker = "Marketing · media"
    page_description = "Uploaded images and videos attachable to posts."
    empty_message = "No media assets have been uploaded yet."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = current_workspace_id(self.request)
        queryset = Media.objects.all()
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        rows = []
        for media in queryset.order_by("-created_at")[:100]:
            rows.append(
                [
                    str(media.pk),
                    media.file.name,
                    media.alt_text,
                    media.created_at.isoformat() if media.created_at else "",
                ]
            )
        context["table_headers"] = ["ID", "File", "Alt text", "Created"]
        context["table_rows"] = rows
        context["table_empty"] = self.empty_message
        return context


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
                "channel_connect_form": ChannelConnectForm(),
                "manual_connect": MANUAL_CONNECT,
                "platform_catalog": platform_catalog(),
                "linkedin_configured": bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET),
                "x_configured": bool(settings.X_CLIENT_ID and settings.X_CLIENT_SECRET),
            }
        )
        return context


def _channel_fragment_context(request: HttpRequest) -> dict:
    return {"channels": channel_rows(request)}


def _connect_panel_context(request: HttpRequest, form: ChannelConnectForm | None = None, **extra) -> dict:
    """Context for the manual-connect panel (form + live channel list)."""
    return {
        "channels": channel_rows(request),
        "channel_connect_form": form or ChannelConnectForm(),
        "manual_connect": MANUAL_CONNECT,
        **extra,
    }


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
    safe_publish_workspace_event(
        channel.workspace_id, "resource.updated", {"resource": "channels", "pk": channel.pk}
    )
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
    from plugins.workers.tasks import broker_gated_send, refresh_oauth_token

    refreshed, error = broker_gated_send(refresh_oauth_token, channel.pk)
    channel.refresh_error = "" if refreshed else f"Refresh queue unavailable: {error}"
    safe_publish_workspace_event(
        channel.workspace_id, "resource.updated", {"resource": "channels", "pk": channel.pk}
    )
    context = _channel_fragment_context(request)
    context["refreshed"] = refreshed
    return render(request, "dashboard/partials/channel_list.html", context)


@login_required
def channel_connect(request: HttpRequest) -> HttpResponse:
    """Create/reconnect a catalog channel by pasting a credential (no OAuth).

    Renders the manual-connect panel on GET and, on a valid POST, upserts the
    workspace-scoped ``SocialChannel`` and swaps the panel (form + list) so the
    new channel appears without a full page load.
    """
    workspace_id = current_workspace_id(request)
    if workspace_id is None:
        return render(
            request,
            "dashboard/partials/channel_connect_panel.html",
            _connect_panel_context(request),
            status=403,
        )
    form = ChannelConnectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        platform = form.cleaned_data["platform"]
        account_name = form.cleaned_data["account_name"].strip()
        channel, created = SocialChannel.objects.update_or_create(
            workspace_id=workspace_id,
            platform=platform,
            account_name=account_name,
            defaults={
                "oauth_token": form.cleaned_data["credential"].strip(),
                "oauth_refresh_token": form.cleaned_data["refresh_token"].strip(),
                "token_expires_at": None,
                "is_active": True,
            },
        )
        safe_publish_workspace_event(
            workspace_id,
            "resource.created" if created else "resource.updated",
            {"resource": "channels", "pk": channel.pk},
        )
        return render(
            request,
            "dashboard/partials/channel_connect_panel.html",
            _connect_panel_context(
                request,
                connected=True,
                connected_verb="Connected" if created else "Reconnected",
                connected_platform=channel.get_platform_display(),
                connected_account=channel.account_name,
            ),
        )
    status = 422 if request.method == "POST" else 200
    return render(
        request,
        "dashboard/partials/channel_connect_panel.html",
        _connect_panel_context(request, form=form),
        status=status,
    )


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
    safe_publish_workspace_event(
        post.workspace_id, "resource.created", {"resource": "posts", "pk": post.pk}
    )
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
        from plugins.workers.tasks import broker_gated_send, publish_post

        queued, error = broker_gated_send(publish_post, post.pk)
        if queued:
            post_error = ""
        else:
            post.status = "failed"
            post.save(update_fields=["status", "updated_at"])
            post_error = f"Publishing queue unavailable: {error}"
    else:
        post_error = ""
    safe_publish_workspace_event(
        post.workspace_id, "resource.updated", {"resource": "posts", "pk": post.pk, "status": post.status}
    )
    return render(request, "dashboard/partials/post_row.html", {"post": post, "post_error": post_error})
