"""
Students API — dashboard, enrollments, progress, profile (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/students.ts
"""

import json
import logging

from django.db.models import F, Sum
from django.shortcuts import get_object_or_404

from plugins.lms.models import Course, Enrollment, Review
from www.api.bolt_adapter import (
    bolt_view, login_required, paginate_queryset, parse_body,
    get_image_url, get_user_display_name,
)

logger = logging.getLogger(__name__)


def _serialize_enrollment(enrollment: Enrollment) -> dict:
    """Serialize an enrollment record."""
    return {
        "id": enrollment.id,
        "course": enrollment.course_id,
        "course_title": enrollment.course.title,
        "course_slug": enrollment.course.slug,
        "course_image": "",
        "status": enrollment.status,
        "progress": enrollment.progress,
        "is_active": enrollment.is_active,
        "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
        "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
        "last_accessed_at": enrollment.last_accessed_at.isoformat() if enrollment.last_accessed_at else None,
        "payment_status": enrollment.payment_status,
    }


# ── Student Dashboard ──

@bolt_view
@login_required
def student_dashboard(request):
    """GET /api/students/dashboard/ — Get student dashboard stats."""
    user = request.user
    enrollments = Enrollment.objects.filter(student=user)

    enrolled_courses = enrollments.count()
    completed_courses = enrollments.filter(status="completed").count()
    active_courses = enrollments.filter(status="active").count()

    total_hours = 0
    try:
        from plugins.lms.models import LessonProgress
        total_seconds = (
            LessonProgress.objects.filter(user=user)
            .aggregate(total=Sum("duration"))["total"] or 0
        )
        total_hours = round(total_seconds / 3600, 1) if total_seconds else 0
    except Exception:
        pass

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


# ── Student Enrollments ──

@bolt_view
def student_enrollments(request, pk=None):
    """GET /api/students/<pk>/enrollments/ — List student's enrollments."""
    user = request.user
    if pk and str(pk) != str(user.id) and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    if pk and str(pk) != str(user.id):
        from django.contrib.auth.models import User
        user = get_object_or_404(User, pk=pk)

    enrollments = Enrollment.objects.filter(student=user).order_by("-enrolled_at")
    page = int(request.GET.get("page", 1))
    items, pagination = paginate_queryset(enrollments, request)

    return {
        "count": pagination["total"],
        "next": None,
        "previous": None,
        "results": [_serialize_enrollment(e) for e in items],
    }


# ── Student Enrollment Detail ──

@bolt_view
@login_required
def student_enrollment_detail(request, pk):
    """GET /api/students/enrollments/<pk>/ — Get enrollment details."""
    enrollment = get_object_or_404(Enrollment, pk=pk, student=request.user)
    data = _serialize_enrollment(enrollment)

    try:
        from plugins.lms.models import LessonProgress
        progress = LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=enrollment.course,
        ).values("lesson_id", "completed", "duration")
        data["lesson_progress"] = list(progress)
    except Exception:
        data["lesson_progress"] = []

    return {"status": "success", "data": data}


# ── Enroll in Course ──

@bolt_view
@login_required
def enroll_in_course(request):
    """POST /api/students/enroll/ — Enroll the current user in a course."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    course_id = body.get("course_id")
    if not course_id:
        return {"status": "error", "message": "course_id is required"}, 400

    course = get_object_or_404(Course, pk=course_id, is_published=True, is_active=True)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return {"status": "error", "message": "Already enrolled in this course"}, 400

    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        status="active",
        payment_status="completed" if course.is_free else "pending",
    )

    Course.objects.filter(pk=course.pk).update(enrolled_count=F("enrolled_count") + 1)

    return {"status": "success", "data": _serialize_enrollment(enrollment)}, 201


# ── Progress Update ──

@bolt_view
@login_required
def progress_update(request):
    """PATCH /api/students/progress/ — Update lesson progress."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    lesson_id = body.get("lesson_id")
    completed = body.get("completed", True)
    duration = body.get("duration", 0)

    if not lesson_id:
        return {"status": "error", "message": "lesson_id is required"}, 400

    try:
        from plugins.lms.models import Lesson, LessonProgress
        lesson = get_object_or_404(Lesson, pk=lesson_id)

        progress, created = LessonProgress.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={"completed": completed, "duration": duration},
        )

        course = lesson.module.course
        total_lessons = course.total_lessons
        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=course,
            completed=True,
        ).count()

        if total_lessons > 0:
            progress_pct = round((completed_lessons / total_lessons) * 100, 1)
            Enrollment.objects.filter(
                student=request.user, course=course
            ).update(progress=progress_pct)

        return {
            "status": "success",
            "data": {"lesson_id": lesson_id, "completed": completed, "created": created},
        }
    except Exception as e:
        logger.error("Progress update error: %s", e)
        return {"status": "error", "message": "Failed to update progress"}, 500


# ── Student Reviews ──

@bolt_view
@login_required
def student_reviews(request):
    """GET /api/students/reviews/ — Get current student's reviews."""
    reviews = Review.objects.filter(profile=request.user).order_by("-created_at")
    return {
        "status": "success",
        "count": reviews.count(),
        "results": [
            {
                "id": r.id,
                "course_id": r.course_id,
                "course_title": r.course.title if r.course else "",
                "rating": r.rating,
                "comment": r.comment or "",
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ],
    }
