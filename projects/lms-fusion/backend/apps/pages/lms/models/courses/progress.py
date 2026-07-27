import logging
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as DefaultBase

from apps.pages.lms.models.courses.specification import Lesson
from apps.pages.lms.models.enrollment import Enrollment

logger = logging.getLogger(__name__)


class ModuleProgress(DefaultBase):
    """
    Track module progress for users.
    """

    class StatusChoices(models.TextChoices):
        NOT_STARTED = 'not_started', _('Not Started')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey("lms.Enrollment", on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey("lms.Module", on_delete=models.CASCADE, related_name='progress')

    # Progress tracking
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_STARTED)
    progress_percentage = models.FloatField(default=0.0)  # 0-100

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    # Metadata
    notes = models.TextField(blank=True)
    time_spent_minutes = models.FloatField(default=0.0)

    class Meta:
        app_label = "lms"
        unique_together = ['enrollment', 'module']
        ordering = ['module__order']
        indexes = [
            models.Index(fields=['enrollment', 'module']),
            models.Index(fields=['status']),
            models.Index(fields=['progress_percentage']),
            models.Index(fields=['completed_at']),
        ]
        verbose_name = _('Module Progress')
        verbose_name_plural = _('Module Progress')

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.module.title}"

    def start(self):
        """Start the module."""
        if self.status == self.StatusChoices.NOT_STARTED:
            self.status = self.StatusChoices.IN_PROGRESS
            self.started_at = timezone.now()
            self.save()

    def complete(self):
        """Mark module as completed."""
        if self.status != self.StatusChoices.COMPLETED:
            self.status = self.StatusChoices.COMPLETED
            self.progress_percentage = 100.0
            self.completed_at = timezone.now()
            self.save()

    def update_progress(self, progress_percentage, time_spent_minutes=0):
        """Update module progress."""
        self.progress_percentage = max(0.0, min(100.0, progress_percentage))

        if time_spent_minutes:
            self.time_spent_minutes += time_spent_minutes

        # Update status based on progress
        if self.progress_percentage >= 100:
            if self.status != self.StatusChoices.COMPLETED:
                self.complete()
        elif self.status == self.StatusChoices.NOT_STARTED:
            self.start()

        self.save()

    def get_lesson_progress_stats(self):
        """Get lesson progress statistics for this module."""
        from ..models.lesson_progress import LessonProgress

        lessons = self.module.lessons.filter(is_active=True)
        total_lessons = lessons.count()

        completed_lessons = LessonProgress.objects.filter(
            user=self.enrollment.student,
            lesson__in=lessons,
            status=LessonProgress.StatusChoices.COMPLETED
        ).count()

        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
            'remaining_lessons': total_lessons - completed_lessons,
        }

    def calculate_progress(self):
        """Calculate module progress from lesson progress."""
        stats = self.get_lesson_progress_stats()
        self.update_progress(stats['progress_percentage'])
        return self.progress_percentage

class LessonProgress(DefaultBase):
    """
    Track lesson progress for users.
    """
    class StatusChoices(models.TextChoices):
        NOT_STARTED = 'not_started', _('Not Started')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        REVIEWED = 'reviewed', _('Reviewed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey("lms.Lesson", on_delete=models.CASCADE, related_name='progress')

    # Progress tracking
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_STARTED)
    progress = models.FloatField(default=0.0)  # 0-100
    time_spent = models.DurationField(default=timezone.timedelta)

    # Assessment
    score = models.FloatField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    best_score = models.FloatField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']
        ordering = ['-last_accessed_at']
        indexes = [
            models.Index(fields=['user', 'lesson']),
            models.Index(fields=['status']),
            models.Index(fields=['completed_at']),
        ]
        verbose_name = _('Lesson Progress')
        verbose_name_plural = _('Lesson Progress')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

    def start(self):
        """Start the lesson."""
        if self.status == self.StatusChoices.NOT_STARTED:
            self.status = self.StatusChoices.IN_PROGRESS
            self.started_at = timezone.now()
            self.save()

    def complete(self, score=None):
        """Mark lesson as completed."""
        if self.status != self.StatusChoices.COMPLETED:
            self.status = self.StatusChoices.COMPLETED
            self.progress = 100.0
            self.completed_at = timezone.now()

            if score is not None:
                self.score = score
                self.attempts += 1

                if self.best_score is None or score > self.best_score:
                    self.best_score = score

            self.save()

            # Update enrollment progress
            try:
                enrollment = Enrollment.objects.get(
                    user=self.user,
                    course=self.lesson.module.course
                )

                # Calculate overall progress
                total_lessons = Lesson.objects.filter(
                    module__course=enrollment.course,
                    is_active=True
                ).count()

                completed_lessons = LessonProgress.objects.filter(
                    user=self.user,
                    lesson__module__course=enrollment.course,
                    status=self.StatusChoices.COMPLETED
                ).count()

                new_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
                enrollment.update_progress(new_progress)

            except Enrollment.DoesNotExist:
                pass

    def update_progress(self, progress, time_spent=None):
        """Update lesson progress."""
        self.progress = max(0.0, min(100.0, progress))

        if time_spent:
            self.time_spent += time_spent

        if self.progress >= 100 and self.status != self.StatusChoices.COMPLETED:
            self.complete()
        elif self.status == self.StatusChoices.NOT_STARTED:
            self.start()

        self.save()
