"""Loop-CRM marketing module — Postiz DNA (social media scheduling).

Campaign groups posts; Post is the schedulable unit published to a connected
SocialChannel; PostAnalytics captures per-post performance so the attribution
engine can weigh marketing touchpoints against closed deals.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import Workspace


class SocialChannel(models.Model):
    """A connected social platform account (OAuth token stored server-side)."""

    PLATFORMS = [
        ("linkedin", "LinkedIn"),
        ("twitter", "Twitter / X"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("tiktok", "TikTok"),
        ("youtube", "YouTube"),
        ("reddit", "Reddit"),
        ("discord", "Discord"),
        ("slack", "Slack"),
        ("bluesky", "Bluesky"),
        ("mastodon", "Mastodon"),
        ("whatsapp", "WhatsApp"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="social_channels")
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    account_name = models.CharField(max_length=255)
    oauth_token = models.TextField(blank=True)
    oauth_refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["platform", "account_name"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "platform", "account_name"], name="uniq_channel_account"),
        ]

    def __str__(self) -> str:
        return f"{self.get_platform_display()} — {self.account_name}"


class Campaign(models.Model):
    """A marketing campaign — the umbrella that posts and (via deals) revenue roll up to."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="owned_campaigns")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workspace", "start_date"])]

    def __str__(self) -> str:
        return self.name


class Media(models.Model):
    """Uploaded image/video asset attachable to posts."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="media_assets")
    file = models.FileField(upload_to="marketing/media/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.file.name


class Post(models.Model):
    """A schedulable social post. Publishing is delegated to a Dramatiq actor."""

    STATUSES = [
        ("draft", "Draft"),
        ("pending_approval", "Pending approval"),
        ("approved", "Approved"),
        ("scheduled", "Scheduled"),
        ("publishing", "Publishing"),
        ("published", "Published"),
        ("failed", "Failed"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="posts")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    channel = models.ForeignKey(SocialChannel, on_delete=models.CASCADE, related_name="posts")
    media = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    content = models.TextField()
    scheduled_at = models.DateTimeField()
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="draft")
    external_id = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["workspace", "scheduled_at"]),
            models.Index(fields=["workspace", "campaign"]),
        ]

    TRANSITIONS = {
        "draft": {"pending_approval"},
        "pending_approval": {"approved", "draft"},
        "approved": {"scheduled", "draft"},
        "scheduled": {"publishing", "draft"},
        "publishing": {"published", "failed"},
        "failed": {"draft", "scheduled"},
        "published": set(),
    }

    def transition_to(self, status: str, *, save: bool = True) -> None:
        """Move through the Postiz-style lifecycle without skipping review."""
        if status not in dict(self.STATUSES):
            raise ValidationError({"status": "Unknown publishing state."})
        if status != self.status and status not in self.TRANSITIONS.get(self.status, set()):
            raise ValidationError({"status": f"Cannot move a {self.status} post to {status}."})
        self.status = status
        if status == "published" and self.published_at is None:
            from django.utils import timezone

            self.published_at = timezone.now()
        if save:
            self.save(update_fields=["status", "published_at", "updated_at"])

    def __str__(self) -> str:
        return self.content[:60]


class PostAnalytics(models.Model):
    """Per-post performance metrics — the raw material for attribution weights."""

    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="analytics")
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fetched_at = models.DateTimeField(auto_now=True)

    @property
    def engagement(self) -> int:
        return self.likes + self.comments + self.shares

    def __str__(self) -> str:
        return f"analytics for {self.post}"
