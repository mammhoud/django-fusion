"""
Data Students API — dashboard, enrollments, progress tracking.

Replaces the DRF StudentViewSet and EnrollmentViewSet.
All endpoints are new — no existing data API equivalents.
"""

from __future__ import annotations

import logging

from django.db.models import Sum, F
from django.shortcuts import get_object_or_404

from www.api.data.helpers import paginate_queryset, parse_body, get_current_user, get_image_url, get_user_display_name
from www.auth import TokenAuthBackend, auth_required

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register student/enrollment handlers on the given BoltAPI instance."""

    # ── GET /apis/students/<pk>/dashboard — student dashboard stats ──
    @bolt.get("/students/<int:pk>/dashboard", **auth_required())
    def student_dashboard(request, pk):
        """GET /apis/students/<pk>/dashboard — Dashboard stats for a student."""
        user = get_current_user(request)
        if user is None or (user.pk != pk and not user.is_staff):
            return {"status": "error", "message": "Permission denied"}, 403

        enrollments = _get_enrollments(user)
        enrolled_courses = enrollments.count()
        completed_courses = enrollments.filter(status="completed").count()
        active_courses = enrollments.filter(status="active").count()

        # Total learning hours from lesson progress
        total_hours = _get_total_hours(user)

        # Recent activity
        recent_activity = list(
            enrollments.order_by("-last_accessed_at")[:5].values(
                "id", "course__title", "progress", "last_accessed_at"
            )
        )

        return {
            "status": "success",
            "data": {
                "enrolled_courses": enrolled_courses,
                "active_courses": active_courses,
                "completed_courses": completed_courses,
                "total_hours": total_hours,
                "recent_activity": recent_activity,
                "upcoming_deadlines": [],
            },
        }

    # ── GET /apis/students/<pk>/enrollments — student enrollments list ──
    @bolt.get("/students/<int:pk>/enrollments", **auth_required())
    def student_enrollments(request, pk):
        """GET /apis/students/<pk>/enrollments — Paginated enrollments."""
        from django.contrib.auth.models import User

        user = get_current_user(request)
        if user is None or (user.pk != pk and not user.is_staff):
            return {"status": "error", "message": "Permission denied"}, 403

        try:
            student = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return {"status": "error", "message": "Student not found"}, 404

        qs = _get_enrollments(student).order_by("-enrolled_at")
        items, pagination = paginate_queryset(qs, request, default_per_page=20)
        data = [_serialize_enrollment(e) for e in items]

        return {"status": "success", "data": data, "pagination": pagination}

    # ── POST /apis/enrollments — create enrollment ──
    @bolt.post("/enrollments", **auth_required())
    def create_enrollment(request):
        """POST /apis/enrollments — Enroll current user in a course."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)
        course_id = body.get("course_id") or body.get("course")

        if not course_id:
            return {"status": "error", "message": "course_id is required"}, 400

        try:
            from plugins.lms.models import Course, Enrollment

            try:
                course = Course.objects.get(pk=course_id, is_published=True, is_active=True)
            except Course.DoesNotExist:
                return {"status": "error", "message": "Course not found"}, 404

            if Enrollment.objects.filter(student=user, course=course).exists():
                return {"status": "error", "message": "Already enrolled in this course"}, 400

            enrollment = Enrollment.objects.create(
                student=user,
                course=course,
                status="active",
                payment_status="completed" if getattr(course, "price", 0) == 0 else "pending",
            )

            # Bump enrolled count
            Course.objects.filter(pk=course.pk).update(enrolled_count=F("enrolled_count") + 1)

            return {"status": "success", "data": _serialize_enrollment(enrollment)}, 201
        except ImportError:
            return {"status": "success", "data": {
                "id": 0, "student": user.pk, "course": course_id,
                "course_title": "", "course_thumbnail": "",
                "progress": 0, "enrolled_at": "", "completed_at": None,
                "is_completed": False,
            }}, 201
        except Exception as exc:
            logger.error(f"Enrollment error: {exc}")
            return {"status": "error", "message": "Enrollment failed"}, 500

    # ── GET /apis/enrollments/<pk>/progress — list progress ──
    @bolt.get("/enrollments/<int:pk>/progress", **auth_required())
    def get_enrollment_progress(request, pk):
        """GET /apis/enrollments/<pk>/progress — List lesson progress for an enrollment."""
        from plugins.lms.models import Enrollment

        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        try:
            enrollment = Enrollment.objects.get(pk=pk, student=user)
        except Enrollment.DoesNotExist:
            return {"status": "error", "message": "Enrollment not found"}, 404

        data = _get_lesson_progress(user, enrollment.course)
        return {"status": "success", "data": data}

    # ── POST /apis/enrollments/<pk>/progress — update progress ──
    @bolt.post("/enrollments/<int:pk>/progress", **auth_required())
    def update_enrollment_progress(request, pk):
        """POST /apis/enrollments/<pk>/progress — Record lesson progress."""
        from plugins.lms.models import Enrollment

        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        try:
            enrollment = Enrollment.objects.get(pk=pk, student=user)
        except Enrollment.DoesNotExist:
            return {"status": "error", "message": "Enrollment not found"}, 404

        body = parse_body(request)
        lesson_id = body.get("lesson_id")
        time_spent = body.get("time_spent", 0)

        if not lesson_id:
            return {"status": "error", "message": "lesson_id is required"}, 400

        try:
            from plugins.lms.models.courses.specification import Lesson
            from plugins.lms.models.courses.progress import LessonProgress

            lesson = get_object_or_404(Lesson, pk=lesson_id)
            progress, created = LessonProgress.objects.update_or_create(
                user=user,
                lesson=lesson,
                defaults={"completed": True, "duration": time_spent},
            )

            # Recalculate enrollment progress percentage
            course = enrollment.course
            total_lessons = getattr(course, "total_lessons", 0) or Lesson.objects.filter(
                module__course=course
            ).count()

            completed_lessons = LessonProgress.objects.filter(
                user=user,
                lesson__module__course=course,
                completed=True,
            ).count()

            if total_lessons > 0:
                progress_pct = round((completed_lessons / total_lessons) * 100, 1)
                Enrollment.objects.filter(
                    student=user, course=course
                ).update(progress=progress_pct)

            return {"status": "success", "created": created}

        except Exception as e:
            logger.error(f"Progress update error: {e}")
            return {"status": "error", "message": "Failed to update progress"}, 500


# ═══════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════


def _get_enrollments(user):
    """Get Enrollment queryset for a user."""
    from plugins.lms.models import Enrollment
    return Enrollment.objects.filter(student=user)


def _get_total_hours(user) -> float:
    """Calculate total learning hours from lesson progress."""
    try:
        from plugins.lms.models.courses.progress import LessonProgress
        total_seconds = (
            LessonProgress.objects.filter(user=user)
            .aggregate(total=Sum("duration"))["total"] or 0
        )
        return round(total_seconds / 3600, 1) if total_seconds else 0
    except Exception as exc:
        logger.warning("LessonProgress not available for user=%s: %s", getattr(user, "pk", "?"), exc)
        return 0


def _get_lesson_progress(user, course) -> list[dict]:
    """Get all lesson progress entries for a user in a course."""
    try:
        from plugins.lms.models.courses.progress import LessonProgress
        progress = LessonProgress.objects.filter(
            user=user,
            lesson__module__course=course,
        ).values("id", "lesson", "lesson__title", "completed", "duration", "created_at")

        return [
            {
                "id": p["id"],
                "lesson": p["lesson"],
                "lesson_title": p["lesson__title"] or "",
                "is_completed": p["completed"],
                "completed_at": None,
                "time_spent": p["duration"] or 0,
            }
            for p in progress
        ]
    except Exception as exc:
        logger.warning("LessonProgress lookup failed for user=%s course=%s: %s", getattr(user, "pk", "?"), getattr(course, "pk", "?"), exc)
        return []


def _serialize_enrollment(enrollment) -> dict:
    """Serialize an Enrollment instance."""
    return {
        "id": enrollment.pk,
        "student": enrollment.student_id,
        "course": enrollment.course_id,
        "course_title": enrollment.course.title if enrollment.course else "",
        "course_thumbnail": get_image_url(enrollment.course.image) if enrollment.course and hasattr(enrollment.course, "image") else "",
        "progress": float(enrollment.progress) if hasattr(enrollment, "progress") and enrollment.progress else 0,
        "enrolled_at": enrollment.enrolled_at.isoformat() if hasattr(enrollment, "enrolled_at") and enrollment.enrolled_at else "",
        "completed_at": enrollment.completed_at.isoformat() if hasattr(enrollment, "completed_at") and enrollment.completed_at else None,
        "is_completed": getattr(enrollment, "status", "") == "completed",
    }
