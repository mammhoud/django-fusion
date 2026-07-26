"""
Notification model for in-app notifications with read/unread status.
Supports real-time polling and notification preferences.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    In-app notification targeting a specific user.
    Created by various system events (enrollment, grading, announcements, etc.)
    and displayed in the frontend notification bell/dropdown.
    """

    class Type(models.TextChoices):
        ENROLLMENT = "enrollment", _("Enrollment")
        COURSE_UPDATE = "course_update", _("Course Update")
        ASSIGNMENT = "assignment", _("Assignment")
        GRADING = "grading", _("Grading")
        QUIZ = "quiz", _("Quiz")
        REVIEW = "review", _("Review")
        ANNOUNCEMENT = "announcement", _("Announcement")
        SYSTEM = "system", _("System")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    notification_type = models.CharField(
        _("Type"),
        max_length=20,
        choices=Type.choices,
        default=Type.SYSTEM,
        db_index=True,
    )
    title = models.CharField(_("Title"), max_length=255)
    message = models.TextField(_("Message"), blank=True, default="")
    link = models.CharField(_("Link"), max_length=500, blank=True, default="")
    is_read = models.BooleanField(_("Is Read"), default=False, db_index=True)
    is_dismissed = models.BooleanField(_("Is Dismissed"), default=False)
    created_at = models.DateTimeField(_("Created At"), default=timezone.now, db_index=True)
    read_at = models.DateTimeField(_("Read At"), null=True, blank=True)

    class Meta:
        app_label = "lms"
        db_table = "lms_notifications"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title} — {self.user}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def mark_as_dismissed(self):
        """Dismiss notification permanently."""
        self.is_dismissed = True
        self.save(update_fields=["is_dismissed"])


class NotificationPreference(models.Model):
    """
    Per-user notification channel preferences.
    Controls what types of notifications and which channels (in-app, email).
    """

    class Frequency(models.TextChoices):
        IMMEDIATE = "immediate", _("Immediate")
        DAILY = "daily", _("Daily Digest")
        WEEKLY = "weekly", _("Weekly Digest")
        NEVER = "never", _("Never")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name=_("User"),
    )

    # Channel toggles
    in_app_notifications = models.BooleanField(_("In-App Notifications"), default=True)
    email_notifications = models.BooleanField(_("Email Notifications"), default=True)

    # Per-type toggles (all default to True)
    enrollment_notifications = models.BooleanField(_("Enrollment Notifications"), default=True)
    course_update_notifications = models.BooleanField(_("Course Update Notifications"), default=True)
    assignment_notifications = models.BooleanField(_("Assignment Notifications"), default=True)
    grading_notifications = models.BooleanField(_("Grading Notifications"), default=True)
    quiz_notifications = models.BooleanField(_("Quiz Notifications"), default=True)
    review_notifications = models.BooleanField(_("Review Notifications"), default=True)
    announcement_notifications = models.BooleanField(_("Announcement Notifications"), default=True)
    system_notifications = models.BooleanField(_("System Notifications"), default=True)

    # Digest frequency
    digest_frequency = models.CharField(
        _("Digest Frequency"),
        max_length=10,
        choices=Frequency.choices,
        default=Frequency.IMMEDIATE,
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        app_label = "lms"
        db_table = "lms_notification_preferences"
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")

    def __str__(self):
        return f"Notification preferences for {self.user}"
