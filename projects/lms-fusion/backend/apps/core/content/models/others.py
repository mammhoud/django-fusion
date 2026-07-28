"""
Fusion CMS — TeamMember, CourseCategory, Token, DataToken models.

Note: ContactSubmission has been intentionally excluded from this file
because backend/www/core/content/models/contact.py already provides
a more comprehensive ContactSubmission implementation.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class TeamMember(index.Indexed, models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    email = models.EmailField(blank=True, default="")
    photo = models.ForeignKey("wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    social_links = models.JSONField(default=dict, blank=True, help_text='{"twitter": "...", "linkedin": "...", "github": "..."}')
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.IntegerField(default=0)

    panels = [
        MultiFieldPanel([FieldPanel("name"), FieldPanel("title"), FieldPanel("email")], heading="Details"),
        FieldPanel("bio"),
        MultiFieldPanel([FieldPanel("photo"), FieldPanel("social_links")], heading="Media"),
        MultiFieldPanel([FieldPanel("is_active"), FieldPanel("sort_order")], heading="Display"),
    ]

    search_fields = [index.SearchField("name", boost=10), index.FilterField("is_active")]

    class Meta:
        app_label = "content"
        verbose_name = _("team member")
        verbose_name_plural = _("team members")
        ordering = ["sort_order", "name"]

    def __str__(self): return f"{self.name} — {self.title}" if self.title else self.name


@register_snippet
class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.IntegerField(default=0)

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("icon"), FieldPanel("description"), FieldPanel("is_active"), FieldPanel("sort_order")]

    class Meta:
        app_label = "content"
        verbose_name = _("course category")
        verbose_name_plural = _("course categories")
        ordering = ["sort_order", "name"]

    @property
    def course_count(self): return self.courses.filter(is_published=True).count()

    def __str__(self): return self.name


class Token(models.Model):
    """Bolt-native token model — stores SHA-256 hash only.

    Distinct from django_fusion.site.interface.auth.models.Token (JWT-based, in tokens table).
    This is a lighter bolt-only token that keeps the raw value out of the database.

    Token types control what the token can do:
      - access:  issued on login, used for API auth (Authorization: Bearer <token>)
      - api:     long-lived API key for service-to-service or programmatic access
      - sync:    device/cloud sync token (not valid for general API auth)
      - refresh: used to obtain new access tokens without re-login

    The ``category`` field is freeform for grouping (e.g. "pos-branch-1", "mobile-app").
    """
    ACCESS = "access"
    API = "api"
    SYNC = "sync"
    REFRESH = "refresh"
    TOKEN_TYPE_CHOICES = [
        (ACCESS, "Access"),
        (API, "API"),
        (SYNC, "Sync"),
        (REFRESH, "Refresh"),
    ]
    # Token types that are valid for authenticating API requests
    AUTH_TYPES = {ACCESS, API}

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auth_tokens")
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    key_prefix = models.CharField(max_length=8, help_text="First 8 chars of raw token for display")
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPE_CHOICES, default=ACCESS, db_index=True)
    category = models.CharField(max_length=50, blank=True, default="", db_index=True, help_text="Freeform grouping label")
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()  # Override with TokenCachedManager if django-fusion installed

    class Meta:
        app_label = "content"
        verbose_name = _("token")
        verbose_name_plural = _("tokens")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["user", "token_type", "created_at"]),
        ]

    @classmethod
    def from_django_fusion_pattern(cls, user, token_type="access", category="") -> tuple["Token", str]:
        """Create a Token following django-fusion's token customization pattern.

        Returns a (Token, raw_token) tuple so the caller can return the raw
        token to the client while storing only the hash.
        """
        import secrets, hashlib
        raw = secrets.token_hex(20)
        token_obj = cls.objects.create(
            user=user,
            token_hash=hashlib.sha256(raw.encode()).hexdigest(),
            key_prefix=raw[:8],
            token_type=token_type,
            category=category,
        )
        return token_obj, raw

    @classmethod
    def validate_raw_token(cls, raw: str, *, accept_types: set[str] | None = None):
        """Look up a Token by raw token string.

        Returns (token_obj, user) or (None, None).
        When ``accept_types`` is given, only tokens of those types are matched
        (e.g. ``{"access", "api"}`` to reject sync/refresh tokens).
        """
        import hashlib
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        qs = cls.objects.select_related("user")
        if accept_types is not None:
            qs = qs.filter(token_type__in=accept_types)
        try:
            token_obj = qs.get(token_hash=token_hash)
            return token_obj, token_obj.user
        except cls.DoesNotExist:
            return None, None

    def is_valid(self) -> bool:
        """Check if token is valid (following django-fusion pattern)."""
        return True  # Bolt tokens don't expire by default

    def update_last_used(self) -> None:
        """Update last used timestamp (following django-fusion pattern)."""
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])

    def __str__(self): return f"[Token:{self.token_type}] {self.key_prefix}… for {self.user}"


class DataToken(models.Model):
    """Tracks synchronized data via a proper GenericForeignKey.

    Links any model instance to a Token for data sync tracking.
    The ``content_object`` GenericForeignKey navigates to the related record,
    and ``snapshot`` optionally stores a JSON serialization for offline/replay.
    """
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="data_tokens")
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    snapshot = models.JSONField(
        default=dict, blank=True,
        help_text="Optional serialized snapshot for offline sync replay",
    )
    is_sync = models.BooleanField(
        default=False, db_index=True,
        help_text="Whether this data has been synced",
    )
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "content"
        verbose_name = _("data token")
        verbose_name_plural = _("data tokens")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token", "is_sync"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def mark_synced(self) -> None:
        """Mark this data token as synced."""
        self.is_sync = True
        self.synced_at = timezone.now()
        self.save(update_fields=["is_sync", "synced_at"])

    def __str__(self): return f"DataToken #{self.id} — {'synced' if self.is_sync else 'pending'}"
