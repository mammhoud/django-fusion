from django.db import models
from django.utils.translation import gettext_lazy as _
from embed_video.fields import EmbedVideoField
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string

from django_grep.pipelines.models import ContentBase


class Video(ContentBase):
    """
    Video content type with Wagtail image chooser integration.
    Provides embeddable video playback and playlist management.
    """

    video_url = EmbedVideoField(
        verbose_name=_("Video URL"),
        help_text=_("Paste a YouTube, Vimeo, or supported video URL."),
    )
    duration = models.IntegerField(
        help_text=_("Duration in seconds"),
        verbose_name=_("Duration"),
    )
    thumbnail = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="video_thumbnails",
        verbose_name=_("Thumbnail"),
        help_text=_("Choose a thumbnail image from the Wagtail image library."),
    )
    is_preview = models.BooleanField(
        default=False,
        verbose_name=_("Is Preview"),
        help_text=_("Mark this video as a preview clip."),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("description"),
        FieldPanel("video_url"),
        FieldPanel("duration"),
        FieldPanel("thumbnail"),  # Wagtail image chooser here
        FieldPanel("is_preview"),
    ]

    def get_next_video(self):
        """Get the next video in the lesson's module (if lessons are linked)."""
        if not hasattr(self, "lesson") or not self.lesson:
            return None
        return (
            Video.objects.filter(lesson__module=self.lesson.module, order__gt=self.order)
            .order_by("order")
            .first()
        )

    @classmethod
    def get_video_playlist(cls, module):
        """Retrieve a playlist of videos for a given module."""
        return cls.objects.filter(lesson__module=module).order_by("lesson__order", "order")

    @property
    def embeddable_link(self):
        """Return the embeddable video iframe HTML."""
        from embed_video.backends import detect_backend

        try:
            backend = detect_backend(self.video_url)
            return backend.get_embed_code()
        except Exception as e:
            return f"Error: {e!s}"

    class Meta:
        db_table = "videos"
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")

    def __str__(self):
        return self.title
