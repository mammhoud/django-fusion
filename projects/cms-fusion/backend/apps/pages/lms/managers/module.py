
from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django_fusion.management.managers.base import BaseManager

logger = logging.getLogger(__name__)
User = get_user_model()

class ModuleManager(BaseManager):
    """
    Enhanced manager for Module model.
    """

    def get_module_completion_stats(self, module, user=None):
        """
        Get completion statistics for a module.

        Args:
            module: Module object
            user: Optional user filter

        Returns:
            Dictionary with statistics
        """
        from apps.pages.accounts.models import LessonProgress

        # Get all lessons in module
        lessons = module.lessons.filter(is_active=True)
        total_lessons = lessons.count()

        # Get completion stats
        if user:
            # User-specific stats
            completed_lessons = LessonProgress.objects.filter(
                lesson__in=lessons,
                user=user,
                status='completed'
            ).count()

            progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

            return {
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'progress': round(progress, 2),
                'is_complete': progress >= 100,
            }
        else:
            # Overall stats
            from django.db.models import Count

            lesson_stats = lessons.annotate(
                completed_count=Count(
                    'progress',
                    filter=models.Q(progress__status='completed')
                )
            ).aggregate(
                total_completions=models.Sum('completed_count'),
                avg_completion_rate=models.Avg(
                    models.F('completed_count') * 100.0 / models.Count('progress')
                )
            )

            return {
                'total_lessons': total_lessons,
                'total_completions': lesson_stats['total_completions'] or 0,
                'avg_completion_rate': round(lesson_stats['avg_completion_rate'] or 0, 2),
            }

    def reorder_modules(self, course, new_order):
        """
        Reorder modules in a course.

        Args:
            course: Course object
            new_order: List of module IDs in new order

        Returns:
            True if successful
        """
        try:
            with transaction.atomic():
                # Get all modules for the course
                modules = self.filter(course=course)

                # Create mapping of module ID to current order
                module_orders = {module.id: module.order for module in modules}

                # Update orders
                for new_index, module_id in enumerate(new_order, 1):
                    if module_id in module_orders:
                        module = modules.get(id=module_id)
                        module.order = new_index
                        module.save(update_fields=['order'])

                # Reorder any remaining modules
                remaining_modules = modules.exclude(id__in=new_order)
                for i, module in enumerate(remaining_modules, len(new_order) + 1):
                    module.order = i
                    module.save(update_fields=['order'])

                return True

        except Exception as e:
            logger.error(f"Error reordering modules: {e}")
            return False

