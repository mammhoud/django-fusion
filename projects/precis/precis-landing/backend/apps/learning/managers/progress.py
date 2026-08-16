from django.db import models


class LessonProgressQuerySet(models.QuerySet):
    """QuerySet helpers for lesson progress lookups."""

    def completed_lesson_ids(self, enrollment):
        return self.filter(
            enrollment=enrollment, completed=True
        ).values_list("lesson_id", flat=True)
