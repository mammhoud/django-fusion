"""
LMS Viewsets for ctc-research.com
===================================

Routable ModelViewsets for the Learning Management System.
These replace manual URL definitions in apps/lms/urls.py for the
new routable-components routing system.

Usage::

    from plugins.lms.viewsets import CourseViewset, EnrollmentViewset
    # Register in apps/projects/routes.py → LMSApp.viewsets
"""

from __future__ import annotations

from django_fusion.comp.routes import ModelViewset, ReadonlyModelViewset


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

    from plugins.lms.models.courses import Course  # noqa: PLC0415 — lazy import avoids circular

    model = Course
    icon = "school"

    # List view
    list_columns = ("title", "instructor", "category", "level", "published")
    list_filter_fields = ("category", "level", "published")
    list_search_fields = ("title", "description")

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated

    def has_add_permission(self, user):
        return user.is_staff

    def has_change_permission(self, user, obj=None):
        return user.is_staff

    def has_delete_permission(self, user, obj=None):
        return user.is_staff


class EnrollmentViewset(ReadonlyModelViewset):
    """
    Read-only list + detail for enrollments (staff only).
    """

    from plugins.lms.models.enrollment import Enrollment  # noqa: PLC0415

    model = Enrollment
    icon = "how_to_reg"

    list_columns = ("student", "course", "enrolled_at", "status")
    list_filter_fields = ("status",)
    list_search_fields = ("student__email", "course__title")

    def has_view_permission(self, user, obj=None):
        return user.is_staff
