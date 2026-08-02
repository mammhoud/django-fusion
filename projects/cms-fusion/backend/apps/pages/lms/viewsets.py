"""
LMS Viewsets for fusion-cms.com
===================================

Routable ModelViewsets for the Learning Management System.
These replace manual URL definitions in apps/lms/urls.py for the
new routable-components routing system.

Usage::

    from apps.pages.lms.viewsets import CourseViewset, EnrollmentViewset
    # Register in apps/pages/lms/application.py → LMSApp.viewsets
"""

from __future__ import annotations

from django_fusion.routes.models.crud import ModelViewset
from django_fusion.routes.models.crud import ReadonlyModelViewset


def _get_course_model():
    """Lazy import to avoid circular deps during module load."""
    from apps.pages.lms.models.courses import Course
    return Course


def _get_enrollment_model():
    """Lazy import to avoid circular deps during module load."""
    from apps.pages.lms.models.enrollment import Enrollment
    return Enrollment


class CourseViewset(ModelViewset):
    """
    Full CRUD interface for LMS courses.

    Generates:
      GET  /app/lms/courses/              → list
      GET  /app/lms/courses/add/          → create form
      POST /app/lms/courses/add/          → create submit
      GET  /app/lms/courses/<pk>/detail/  → detail
      GET  /app/lms/courses/<pk>/change/  → update form
      POST /app/lms/courses/<pk>/change/  → update submit
      GET  /app/lms/courses/<pk>/delete/  → delete confirm
      POST /app/lms/courses/<pk>/delete/  → delete submit
    """

    # Model will be resolved lazily during initialization to avoid circular imports
    model = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.__class__.model is None:
            from apps.pages.lms.models.courses import Course
            self.__class__.model = Course

    icon = "school"

    # List view
    list_columns = ("title", "instructor", "category", "level", "published")
    list_filter_fields = ("category", "level", "published")
    list_search_fields = ("title", "description")

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated

    def has_add_permission(self, user):
        return user.is_staff


class EnrollmentViewset(ModelViewset):
    """Full CRUD interface for LMS course enrollments."""

    model = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.__class__.model is None:
            from apps.pages.lms.models.enrollment import Enrollment
            self.__class__.model = Enrollment

    icon = "people"

    list_columns = ("user", "course", "status", "enrolled_at", "completed_at")
    list_filter_fields = ("status", "enrolled_at", "completed_at")
    list_search_fields = ("user__username", "user__email", "course__title")

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated

    def has_change_permission(self, user, obj=None):
        return user.is_staff or (obj and obj.user_id == user.id)
