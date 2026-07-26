"""
Announcement model for the LMS — Wagtail-managed announcements targeting
instructors, students, or both. Served via REST API to the frontend dashboard.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Announcement(models.Model):
    """A CMS-managed announcement displayed on the dashboard."""

    AUDIENCE_CHOICES = [
        ("all", _("All Users")),
        ("instructor", _("Instructors Only")),
        ("student", _("Students Only")),
    ]

    title = models.CharField(max_length=300, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))
    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default="all",
        verbose_name=_("Target Audience"),
    )
    link = models.URLField(
        blank=True, default="",
        help_text=_("Optional link for 'Learn More' button"),
        verbose_name=_("Link URL"),
    )
    link_label = models.CharField(
        max_length=100, blank=True, default="",
        help_text=_("Button label for the link (e.g., 'View Course')"),
        verbose_name=_("Link Label"),
    )
    is_published = models.BooleanField(default=False, verbose_name=_("Published"))
    published_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Published At"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    sort_order = models.IntegerField(default=0, verbose_name=_("Sort Order"))

    panels = [
        FieldPanel("title"),
        FieldPanel("content"),
        FieldPanel("audience"),
        FieldPanel("link"),
        FieldPanel("link_label"),
        FieldPanel("is_published"),
        FieldPanel("published_at"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        app_label = "lms"
        ordering = ["sort_order", "-published_at", "-created_at"]
        verbose_name = _("announcement")
        verbose_name_plural = _("announcements")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
