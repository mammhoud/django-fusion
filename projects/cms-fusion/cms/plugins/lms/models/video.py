"""
Video Model for LMS — tracks uploaded video files with metadata.

Supports:
- File upload with configurable storage paths
- Background processing status (pending → processing → ready / failed)
- Metadata extraction (duration, resolution, format, file_size)
- Thumbnail generation
- Captions/subtitles support
- Access control (free preview vs. enrollment-only)
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _video_upload_path(instance: "Video", filename: str) -> str:
    """Generate upload path: ``lesson_videos/<course_id>/<uuid>_<filename>``.

    Organises videos by course for easy cleanup and S3 prefix navigation.
    Safe-guards against None lesson/module/course chains.
    """
    course = getattr(getattr(getattr(instance, "lesson", None), "module", None), "course", None)
    course_id = getattr(course, "id", "unknown") if course else "unknown"
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex[:12]}{ext}"
    return f"lesson_videos/course_{course_id}/{unique_name}"


def _thumbnail_upload_path(instance: "Video", filename: str) -> str:
    """Generate upload path for video thumbnails."""
    ext = Path(filename).suffix.lower() or ".jpg"
    return f"lesson_thumbnails/video_{instance.id or 'new'}{ext}"


def _caption_upload_path(instance: "Video", filename: str) -> str:
    """Generate upload path for caption/subtitle files.

    For ``VideoCaption`` instances, uses ``instance.video_id`` so captions
    are grouped under the parent video's directory.
    """
    video_id = getattr(instance, "video_id", None) or instance.id or "new"
    return f"lesson_captions/video_{video_id}/{filename}"


class Video(models.Model):
    """A video file associated with an LMS lesson.

    Tracks the full lifecycle from upload through processing to delivery,
    with metadata extracted during processing so the frontend can display
    duration, resolution, and format information without probing the file.
    """

    class ProcessingStatus(models.TextChoices):
        PENDING = "pending", _("Pending Processing")
        PROCESSING = "processing", _("Processing")
        READY = "ready", _("Ready")
        FAILED = "failed", _("Failed")

    class VideoFormat(models.TextChoices):
        MP4 = "mp4", _("MP4 (H.264)")
        WEBM = "webm", _("WebM (VP9)")
        OGG = "ogg", _("Ogg (Theora)")
        OTHER = "other", _("Other")

    # ── Core ──
    lesson = models.ForeignKey(
        "lms.Lesson",
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name=_("Lesson"),
        help_text=_("The lesson this video belongs to"),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Display title for the video"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Optional description shown below the video player"),
    )

    # ── File ──
    file = models.FileField(
        upload_to=_video_upload_path,
        verbose_name=_("Video File"),
        help_text=_("Upload the video file (MP4 recommended, max 2GB)"),
    )
    thumbnail = models.ImageField(
        upload_to=_thumbnail_upload_path,
        blank=True, null=True,
        verbose_name=_("Thumbnail"),
        help_text=_("Auto-generated or custom preview image"),
    )
    captions = models.FileField(
        upload_to=_caption_upload_path,
        blank=True, null=True,
        verbose_name=_("Captions / Subtitles"),
        help_text=_("VTT or SRT subtitle file"),
    )

    # ── Metadata (populated during processing) ──
    duration_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Duration (seconds)"),
        help_text=_("Video duration in seconds (auto-detected)"),
    )
    width = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Width (px)"),
    )
    height = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Height (px)"),
    )
    file_size = models.BigIntegerField(
        default=0,
        verbose_name=_("File Size (bytes)"),
        editable=False,
    )
    video_format = models.CharField(
        max_length=10,
        choices=VideoFormat.choices,
        default=VideoFormat.MP4,
        verbose_name=_("Video Format"),
    )
    bitrate = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Bitrate (kbps)"),
        help_text=_("Average video bitrate"),
    )

    # ── Processing ──
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        db_index=True,
        verbose_name=_("Processing Status"),
    )
    processing_error = models.TextField(
        blank=True,
        verbose_name=_("Processing Error"),
        help_text=_("Error message if processing failed"),
    )
    processing_started_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Processing Started"),
    )
    processed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Processed At"),
    )

    # ── Access ──
    is_preview = models.BooleanField(
        default=False,
        verbose_name=_("Free Preview"),
        help_text=_("Allow viewing without course enrollment"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Hide from students without deleting"),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sort Order"),
        help_text=_("Order among multiple videos in a lesson"),
    )

    # ── Timestamps ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "lms"
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
        ordering = ["sort_order", "created_at"]
        indexes = [
            models.Index(fields=["lesson", "sort_order"]),
            models.Index(fields=["processing_status"]),
            models.Index(fields=["is_active", "is_preview"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_video_format_display()}, {self.duration_display})"

    # ── Properties ──

    @property
    def duration_display(self) -> str:
        """Human-readable duration string."""
        total = self.duration_seconds
        if total == 0:
            return "0:00"
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @property
    def duration_minutes(self) -> int:
        """Duration in whole minutes (for course catalog display)."""
        return max(1, round(self.duration_seconds / 60))

    @property
    def resolution_display(self) -> str:
        """Human-readable resolution (e.g. '1920×1080')."""
        if self.width and self.height:
            return f"{self.width}×{self.height}"
        return ""

    @property
    def file_size_display(self) -> str:
        """Human-readable file size."""
        size = self.file_size
        if size == 0:
            return "0 B"
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def streaming_url(self) -> str:
        """Absolute URL for streaming this video."""
        if not self.pk:
            return ""
        from django.urls import reverse
        return reverse("lms:video-stream", kwargs={"video_id": self.pk})

    # ── Methods ──

    def save(self, *args, **kwargs):
        """Auto-capture file_size and set default title."""
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                pass
        if not self.title:
            self.title = Path(self.file.name).stem.replace("_", " ").replace("-", " ").title() if self.file else "Untitled"
        super().save(*args, **kwargs)

    def mark_processing(self) -> None:
        """Mark video as currently being processed."""
        self.processing_status = self.ProcessingStatus.PROCESSING
        self.processing_started_at = timezone.now()
        self.save(update_fields=["processing_status", "processing_started_at", "updated_at"])

    def mark_ready(self, duration: int = 0, width: int = 0, height: int = 0,
                   bitrate: int = 0, fmt: str = "mp4") -> None:
        """Mark video as processed and ready for streaming."""
        self.processing_status = self.ProcessingStatus.READY
        self.processed_at = timezone.now()
        self.duration_seconds = duration
        self.width = width
        self.height = height
        self.bitrate = bitrate
        self.video_format = fmt
        self.save(update_fields=[
            "processing_status", "processed_at",
            "duration_seconds", "width", "height",
            "bitrate", "video_format", "updated_at",
        ])

    def mark_failed(self, error: str) -> None:
        """Mark video processing as failed with error message."""
        self.processing_status = self.ProcessingStatus.FAILED
        self.processing_error = error
        self.processed_at = timezone.now()
        self.save(update_fields=["processing_status", "processing_error", "processed_at", "updated_at"])


class VideoCaption(models.Model):
    """Individual caption/subtitle track for a video.

    Supports multiple languages and formats (VTT, SRT).
    """

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="caption_tracks",
        verbose_name=_("Video"),
    )
    language = models.CharField(
        max_length=10,
        default="en",
        verbose_name=_("Language Code"),
        help_text=_("BCP 47 language code (e.g. 'en', 'fr', 'ar')"),
    )
    label = models.CharField(
        max_length=50,
        default="English",
        verbose_name=_("Label"),
        help_text=_("Display label (e.g. 'English', 'French')"),
    )
    file = models.FileField(
        upload_to=_caption_upload_path,
        verbose_name=_("Caption File"),
        help_text=_("WebVTT (.vtt) or SubRip (.srt) file"),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default Track"),
        help_text=_("Play by default when captions are enabled"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "lms"
        verbose_name = _("Video Caption")
        verbose_name_plural = _("Video Captions")
        unique_together = [["video", "language"]]

    def __str__(self) -> str:
        return f"{self.label} ({self.language}) — {self.video.title}"
