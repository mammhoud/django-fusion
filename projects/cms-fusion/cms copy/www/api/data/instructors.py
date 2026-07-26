"""
Data Instructors API — list, detail (with courses/reviews), dashboard stats, courses list, reviews list, profile update.

Replaces the DRF InstructorViewSet and InstructorCourseDeleteViewSet.
All endpoints are new — no existing data API equivalents beyond the basic
``/apis/lms/instructors`` list.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum
from django.utils import timezone

from www.api.data.helpers import paginate_queryset, parse_body, get_current_user, get_image_url, get_user_display_name
from www.auth import TokenAuthBackend, auth_required

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register instructor handlers on the given BoltAPI instance."""

    # ── GET /apis/instructors — list instructors (rich, with stats) ──
    @bolt.get("/instructors")
    def list_instructors(request):
        """GET /apis/instructors — Paginated instructor list with stats."""
        qs = User.objects.filter(groups__name="Instructors", is_active=True)
        qs = qs.order_by("first_name", "last_name")

        items, pagination = paginate_queryset(qs, request, default_per_page=20)
        data = [_serialize_instructor(u) for u in items]

        return {"status": "success", "data": data, "pagination": pagination}

    # ── GET /apis/instructors/<pk> — instructor detail with courses ──
    @bolt.get("/instructors/<int:pk>")
    def get_instructor(request, pk):
        """GET /apis/instructors/<pk> — Single instructor detail with courses."""
        try:
            user = User.objects.get(pk=pk, is_active=True)
        except User.DoesNotExist:
            return {"status": "error", "message": "Instructor not found"}, 404

        data = _serialize_instructor(user)
        data["courses"] = _get_instructor_courses(user)
        data["social"] = {"website": "", "twitter": "", "github": ""}

        return {"status": "success", "data": data}

    # ── PATCH /apis/instructors/<pk> — update instructor profile ──
    @bolt.patch("/instructors/<int:pk>", **auth_required())
    def update_instructor(request, pk):
        """PATCH /apis/instructors/<pk> — Update instructor profile (own or staff)."""
        current_user = get_current_user(request)
        if current_user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        if current_user.pk != pk and not current_user.is_staff:
            return {"status": "error", "message": "Permission denied"}, 403

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return {"status": "error", "message": "Instructor not found"}, 404

        body = parse_body(request)

        # Build update_fields dynamically so bio is saved when present
        update_fields = []
        for field in ["first_name", "last_name", "email"]:
            if field in body and body[field] is not None:
                setattr(user, field, str(body[field]).strip())
                update_fields.append(field)

        bio_val = body.get("bio")
        if bio_val is not None and hasattr(user, "bio"):
            user.bio = bio_val
            update_fields.append("bio")

        if update_fields:
            user.save(update_fields=update_fields)

        return {"status": "success", "data": _serialize_instructor(user)}

    # ── GET /apis/instructors/<pk>/dashboard — instructor dashboard stats ──
    @bolt.get("/instructors/<int:pk>/dashboard", **auth_required())
    def instructor_dashboard(request, pk):
        """GET /apis/instructors/<pk>/dashboard — Stats and metrics for instructor."""
        current_user = get_current_user(request)
        if current_user is None or (current_user.pk != pk and not current_user.is_staff):
            return {"status": "error", "message": "Permission denied"}, 403

        from plugins.lms.models import Course, Enrollment
        from plugins.lms.models.review import Review

        courses = Course.objects.filter(instructor_id=pk)
        published_courses = courses.filter(is_published=True)
        enrollments = Enrollment.objects.filter(course__instructor_id=pk)

        total_revenue = float(
            enrollments.filter(payment_status="completed").aggregate(
                total=Sum("amount_paid")
            )["total"] or 0
        )

        # Monthly earnings
        monthly_earnings = list(
            enrollments.filter(payment_status="completed")
            .extra(select={"month": "strftime('%%Y-%%m', enrolled_at)"})
            .values("month")
            .annotate(amount=Sum("amount_paid"))
            .order_by("month")[:12]
        )

        # Popular courses
        popular_courses = list(
            published_courses.annotate(
                student_count=Count("enrollments"),
                course_revenue=Sum("enrollments__amount_paid"),
            ).order_by("-student_count")[:5].values(
                "id", "title", "student_count", "course_revenue"
            )
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

    # ── GET /apis/instructors/<pk>/courses — instructor's courses ──
    @bolt.get("/instructors/<int:pk>/courses")
    def instructor_courses(request, pk):
        """GET /apis/instructors/<pk>/courses — List courses by this instructor."""
        from plugins.lms.models import Course

        courses = Course.objects.filter(instructor_id=pk).order_by("-created_at")
        data = [_serialize_course_minimal(c) for c in courses]

        return {"status": "success", "count": len(data), "results": data}

    # ── GET /apis/instructors/<pk>/reviews — instructor's reviews ──
    @bolt.get("/instructors/<int:pk>/reviews")
    def instructor_reviews(request, pk):
        """GET /apis/instructors/<pk>/reviews — Paginated reviews."""
        from plugins.lms.models.review import Review

        reviews = Review.objects.filter(course__instructor_id=pk).order_by("-created_at")
        items, pagination = paginate_queryset(reviews, request, default_per_page=20)

        data = [
            {
                "id": r.id,
                "student": get_user_display_name(r.profile) if hasattr(r, "profile") and r.profile else "",
                "student_avatar": "",
                "course": r.course.title if r.course else "",
                "course_id": r.course_id,
                "rating": r.rating,
                "text": getattr(r, "comment", "") or "",
                "date": r.created_at.isoformat() if hasattr(r, "created_at") and r.created_at else None,
                "helpful": 0,
                "replied": False,
            }
            for r in items
        ]

        return {"status": "success", "count": len(data), "results": data, "pagination": pagination}

    # ── DELETE /apis/instructors/courses/<pk> — delete an instructor's course ──
    @bolt.delete("/instructors/courses/<int:pk>", **auth_required())
    def delete_instructor_course(request, pk):
        """DELETE /apis/instructors/courses/<pk> — Delete a course (owner only)."""
        current_user = get_current_user(request)
        if current_user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        from plugins.lms.models import Course

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return {"status": "error", "message": "Course not found"}, 404

        if course.instructor_id != current_user.pk and not current_user.is_staff:
            return {"status": "error", "message": "Permission denied"}, 403

        course.delete()
        return {"status": "success", "message": "Course deleted"}


# ═══════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════


def _serialize_instructor(user) -> dict:
    """Serialize a User (instructor) into the instructor response shape."""
    from plugins.lms.models import Course, Enrollment
    from plugins.lms.models.review import Review

    expertise = []
    try:
        from plugins.lms.models.courses.detail import Specialization
        expertise = list(
            Specialization.objects.filter(
                courses__instructor=user, is_active=True
            ).distinct().values_list("title", flat=True)[:10]
        )
    except Exception as exc:
        logger.debug("Specialization lookup not available for instructor=%s: %s", user.pk, exc)

    courses_count = Course.objects.filter(instructor=user, is_published=True).count()
    students_count = (
        Enrollment.objects.filter(course__instructor=user)
        .values("student").distinct().count()
    )
    total_reviews = Review.objects.filter(course__instructor=user).count()
    avg_rating = Review.objects.filter(course__instructor=user).aggregate(
        avg=Avg("rating")
    )["avg"] or 0

    bio = getattr(user, "bio", "")

    return {
        "id": user.pk,
        "user": user.pk,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": "",
        "title": "Instructor" if user.groups.filter(name="Instructors").exists() else "",
        "bio": bio if bio else "",
        "expertise": expertise,
        "courses_count": courses_count,
        "students_count": students_count,
        "total_reviews": total_reviews,
        "average_rating": float(avg_rating),
        "joined_at": user.date_joined.isoformat() if user.date_joined else None,
    }


def _get_instructor_courses(user) -> list[dict]:
    """Get serialized courses for an instructor."""
    try:
        from plugins.lms.models import Course
        courses = Course.objects.filter(
            instructor=user, is_published=True, is_active=True
        ).order_by("-created_at")

        return [
            {
                "id": c.pk,
                "title": c.title,
                "slug": getattr(c, "slug", ""),
                "short_description": getattr(c, "short_description", ""),
                "price": float(getattr(c, "price", 0)),
                "thumbnail": get_image_url(getattr(c, "image", None)),
                "duration": getattr(c, "duration", ""),
                "level": getattr(c, "skill_level", "beginner"),
                "students_count": getattr(c, "enrolled_count", 0),
                "rating": float(getattr(c, "rating", 0)),
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in courses
        ]
    except Exception as exc:
        logger.warning("Instructor courses lookup failed for user=%s: %s", user.pk, exc)
        return []


def _serialize_course_minimal(course) -> dict:
    """Minimal course serialization for the instructor's courses list."""
    return {
        "id": course.pk,
        "title": course.title,
        "slug": getattr(course, "slug", ""),
        "short_description": getattr(course, "short_description", ""),
        "price": float(getattr(course, "price", 0)),
        "thumbnail": get_image_url(getattr(course, "image", None)) if hasattr(course, "image") else "",
        "duration": getattr(course, "duration", ""),
        "level": getattr(course, "skill_level", "beginner"),
        "students_count": getattr(course, "enrolled_count", 0),
        "rating": float(getattr(course, "rating", 0)),
        "is_published": getattr(course, "is_published", True),
        "created_at": course.created_at.isoformat() if course.created_at else None,
    }
