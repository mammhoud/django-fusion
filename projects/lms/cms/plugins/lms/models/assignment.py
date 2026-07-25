"""
Assignment and AssignmentSubmission models for the LMS.

Assignments are created by instructors for specific courses.
Submissions are uploaded or written by students and graded by instructors.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Assignment(models.Model):
    """A course assignment created by an instructor."""

    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("Course"),
    )
    title = models.CharField(max_length=300, verbose_name=_("Title"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))
    instructions = models.TextField(blank=True, default="", verbose_name=_("Instructions"))
    due_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Due Date")
    )
    max_score = models.IntegerField(default=100, verbose_name=_("Maximum Score"))
    is_published = models.BooleanField(default=True, verbose_name=_("Published"))
    sort_order = models.IntegerField(default=0, verbose_name=_("Sort Order"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    panels = [
        FieldPanel("course"),
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("instructions"),
        FieldPanel("due_date"),
        FieldPanel("max_score"),
        FieldPanel("is_published"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        app_label = "lms"
        ordering = ["course", "sort_order", "-created_at"]
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")

    def __str__(self):
        return f"{self.title} — {self.course.title}"


class AssignmentSubmission(models.Model):
    """A student's submission for an assignment."""

    STATUS_CHOICES = [
        ("submitted", _("Submitted")),
        ("graded", _("Graded")),
        ("returned", _("Returned for Revision")),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name=_("Assignment"),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
        verbose_name=_("Student"),
    )
    text_submission = models.TextField(
        blank=True, default="", verbose_name=_("Text Submission")
    )
    file_url = models.URLField(
        blank=True, default="", verbose_name=_("File URL")
    )
    file_name = models.CharField(
        max_length=500, blank=True, default="", verbose_name=_("File Name")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="submitted",
        verbose_name=_("Status"),
    )
    score = models.IntegerField(
        null=True, blank=True, verbose_name=_("Score")
    )
    feedback = models.TextField(
        blank=True, default="", verbose_name=_("Instructor Feedback")
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions",
        verbose_name=_("Graded By"),
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Submitted At"))
    graded_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Graded At")
    )

    panels = [
        FieldPanel("assignment"),
        FieldPanel("student"),
        FieldPanel("text_submission"),
        FieldPanel("file_url"),
        FieldPanel("status"),
        FieldPanel("score"),
        FieldPanel("feedback"),
    ]

    class Meta:
        app_label = "lms"
        ordering = ["-submitted_at"]
        unique_together = ["assignment", "student"]
        verbose_name = _("assignment submission")
        verbose_name_plural = _("assignment submissions")

    def __str__(self):
        return f"{self.student.username} — {self.assignment.title}"

    @property
    def is_graded(self) -> bool:
        return self.status == "graded" and self.score is not None

    def save(self, *args, **kwargs):
        if self.status == "graded" and not self.graded_at:
            self.graded_at = timezone.now()
        super().save(*args, **kwargs)
