"""
Instructors API — list, detail, dashboard, courses, reviews (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/instructors.ts
"""

import json
import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from plugins.lms.models import Course, Enrollment, Review
from www.api.data_adapter import (
    bolt_view, login_required, paginate_queryset, parse_body,
    get_image_url, get_user_display_name,
)
from www.api.courses import _serialize_course

logger = logging.getLogger(__name__)


def _serialize_instructor(user: User) -> dict:
    """Serialize a User to the instructor format expected by the frontend."""
    courses_qs = Course.objects.filter(instructor=user, is_published=True)
    reviews_agg = Review.objects.filter(course__instructor=user).aggregate(
        avg_rating=Avg("rating"), total=Count("id")
    )

    return {
        "id": user.id,
        "user": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": "",
        "title": "Instructor" if user.groups.filter(name="Instructors").exists() else "",
        "bio": getattr(user, "bio", ""),
        "expertise": [],
        "courses_count": courses_qs.count(),
        "students_count": (
            Enrollment.objects.filter(course__instructor=user)
            .values("student").distinct().count()
        ),
        "total_reviews": reviews_agg["total"] or 0,
        "average_rating": float(reviews_agg["avg_rating"] or 0),
        "joined_at": user.date_joined.isoformat() if user.date_joined else None,
    }


# ── Instructor List ──

@bolt_view
def instructor_list(request):
    """GET /api/instructors/ — List all instructors."""
    instructors = User.objects.filter(
        groups__name="Instructors", is_active=True,
    ).order_by("first_name", "last_name")

    page = int(request.GET.get("page", 1))
    items, pagination = paginate_queryset(instructors, request)

    return {
        "count": pagination["total"],
        "next": None,
        "previous": None,
        "results": [_serialize_instructor(u) for u in items],
    }


# ── Instructor Detail ──

@bolt_view
def instructor_detail(request, pk):
    """GET /api/instructors/<pk>/ — Get instructor profile details."""
    user = get_object_or_404(User, pk=pk, is_active=True)
    data = _serialize_instructor(user)

    courses = Course.objects.filter(instructor=user, is_published=True, is_active=True)
    data["courses"] = [_serialize_course(c) for c in courses]

    try:
        from plugins.lms.models import Specialization
        specializations = Specialization.objects.filter(
            courses__instructor=user, is_active=True
        ).distinct().values_list("title", flat=True)
        data["expertise"] = list(specializations)[:10]
    except Exception:
        pass

    data["social"] = {"website": "", "twitter": "", "github": ""}

    return {"status": "success", "data": data}


# ── Instructor Dashboard ──

@bolt_view
@login_required
def instructor_dashboard(request, pk):
    """GET /api/instructors/<pk>/dashboard/ — Get instructor analytics."""
    if str(pk) != str(request.user.id) and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    user = get_object_or_404(User, pk=pk)
    courses = Course.objects.filter(instructor=user)
    published_courses = courses.filter(is_published=True)
    enrollments = Enrollment.objects.filter(course__instructor=user)

    total_revenue = float(
        enrollments.filter(payment_status="completed").aggregate(
            total=Sum("amount_paid")
        )["total"] or 0
    )

    monthly_earnings = list(
        enrollments.filter(payment_status="completed")
        .extra(select={"month": "strftime('%%Y-%%m', enrolled_at)"})
        .values("month").annotate(amount=Sum("amount_paid"))
        .order_by("month")[:12]
    )

    popular_courses = list(
        published_courses.annotate(
            student_count=Count("enrollments"),
            course_revenue=Sum("enrollments__amount_paid"),
        ).order_by("-student_count")[:5].values("id", "title", "student_count", "course_revenue")
    )

    avg_rating = Review.objects.filter(course__in=published_courses).aggregate(
        avg=Avg("rating")
    )["avg"] or 0

    recent_enrollments = enrollments.filter(
        enrolled_at__gte=timezone.now() - timedelta(days=30)
    ).count()

    return {
        "status": "success",
        "data": {
            "total_courses": published_courses.count(),
            "total_students": enrollments.values("student").distinct().count(),
            "total_revenue": total_revenue,
            "average_rating": float(avg_rating),
            "recent_enrollments": recent_enrollments,
            "pending_reviews": Review.objects.filter(
                course__in=published_courses, is_displayed=False
            ).count(),
            "monthly_earnings": monthly_earnings,
            "popular_courses": popular_courses,
        },
    }


# ── Instructor Courses ──

@bolt_view
@login_required
def instructor_courses(request, pk):
    """GET /api/instructors/<pk>/courses/ — List courses by instructor."""
    instructor = get_object_or_404(User, pk=pk)
    courses = Course.objects.filter(instructor=instructor).order_by("-created_at")
    return {
        "status": "success",
        "count": courses.count(),
        "results": [_serialize_course(c) for c in courses],
    }


# ── Instructor Reviews ──

@bolt_view
@login_required
def instructor_reviews(request, pk):
    """GET /api/instructors/<pk>/reviews/ — List reviews for instructor's courses."""
    instructor = get_object_or_404(User, pk=pk)
    reviews = Review.objects.filter(course__instructor=instructor).order_by("-created_at")
    items, pagination = paginate_queryset(reviews, request)

    return {
        "count": pagination["total"],
        "next": None,
        "previous": None,
        "results": [
            {
                "id": r.id,
                "student": get_user_display_name(r.profile) if r.profile else "",
                "student_avatar": "",
                "course": r.course.title if r.course else "",
                "course_id": r.course_id,
                "rating": r.rating,
                "text": r.comment or "",
                "date": r.created_at.isoformat() if r.created_at else None,
                "helpful": 0,
                "replied": False,
            }
            for r in items
        ],
    }


# ── Update Instructor Profile ──

@bolt_view
@login_required
def instructor_profile_update(request, pk):
    """PATCH /api/instructors/<pk>/ — Update instructor profile."""
    if str(pk) != str(request.user.id) and not request.user.is_staff:
        return {"status": "error", "message": "Permission denied"}, 403

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    user = request.user
    allowed_fields = {"first_name", "last_name", "email", "bio"}
    for field in allowed_fields:
        if field in body:
            setattr(user, field, body[field])
    user.save(update_fields=[f for f in allowed_fields if f in body])

    return {"status": "success", "data": _serialize_instructor(user)}


# ── Delete Course ──

@bolt_view
@login_required
def instructor_delete_course(request, pk):
    """DELETE /api/instructors/courses/<pk>/ — Delete a course (instructor only)."""
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    course.delete()
    return {"status": "success", "message": "Course deleted"}
