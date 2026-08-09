from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .specification import Lesson
from apps.learning.managers.progress import LessonProgressQuerySet


class ModuleProgress(models.Model):
    """Track a learner's progress through a single course module (Precis parity)."""

    class StatusChoices(models.TextChoices):
        NOT_STARTED = "not_started", _("Not Started")
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")

    enrollment = models.ForeignKey(
        "learning.Enrollment",
        on_delete=models.CASCADE,
        related_name="module_progress",
    )
    module = models.ForeignKey(
        "learning.Module", on_delete=models.CASCADE, related_name="progress"
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NOT_STARTED,
    )
    progress_percentage = models.FloatField(default=0.0)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    notes = models.TextField(blank=True)
    time_spent_minutes = models.FloatField(default=0.0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "module"], name="learning_enrollment_module"
            )
        ]
        ordering = ["module__order"]
        indexes = [
            models.Index(fields=["enrollment", "module"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.enrollment.user} — {self.module.title}"

    def start(self):
        """Mark the module as in progress."""
        if self.status == self.StatusChoices.NOT_STARTED:
            self.status = self.StatusChoices.IN_PROGRESS
            self.started_at = timezone.now()
            self.save(update_fields=["status", "started_at", "last_accessed_at"])

    def complete(self):
        """Mark the module as completed (100%)."""
        if self.status != self.StatusChoices.COMPLETED:
            self.status = self.StatusChoices.COMPLETED
            self.progress_percentage = 100.0
            self.completed_at = timezone.now()
            self.save(update_fields=["status", "progress_percentage", "completed_at", "last_accessed_at"])

    def update_progress(self, progress_percentage: float, time_spent_minutes: float = 0):
        """Update progress percentage and derive status."""
        self.progress_percentage = max(0.0, min(100.0, progress_percentage))
        if time_spent_minutes:
            self.time_spent_minutes += time_spent_minutes

        if self.progress_percentage >= 100 and self.status != self.StatusChoices.COMPLETED:
            self.complete()
            return
        if self.progress_percentage > 0 and self.status == self.StatusChoices.NOT_STARTED:
            self.start()
        self.save(update_fields=["progress_percentage", "time_spent_minutes", "last_accessed_at"])

    def get_lesson_progress_stats(self) -> dict:
        """Lesson completion stats for the module's lessons."""
        lessons = self.module.lessons.filter(is_active=True)
        total_lessons = lessons.count()
        completed_lessons = self.enrollment.lesson_progress.filter(
            lesson__in=lessons, completed=True
        ).count()
        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": (completed_lessons / total_lessons * 100) if total_lessons else 0.0,
            "remaining_lessons": total_lessons - completed_lessons,
        }

    def calculate_progress(self) -> float:
        """Recompute module progress from lesson completions."""
        stats = self.get_lesson_progress_stats()
        self.update_progress(stats["progress_percentage"])
        return self.progress_percentage


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(
        "learning.Enrollment", on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="learner_progress")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"], name="learning_enrollment_lesson"
            )
        ]

    objects = LessonProgressQuerySet.as_manager()

    def set_completed(self, completed: bool = True):
        self.completed = completed
        self.completed_at = timezone.now() if completed else None
        self.save(update_fields=["completed", "completed_at", "updated_at"])
