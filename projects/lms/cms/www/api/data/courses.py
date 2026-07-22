"""
Data Courses API — list, detail (full with modules/lessons), featured, categories.

Extends the existing bolt course endpoints in ``apis.py`` (which provide
basic list/detail) with additional detail depth and a featured endpoint.
"""

from __future__ import annotations

import logging

from www.api.data.helpers import paginate_queryset, get_image_url, get_user_display_name

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register course handlers on the given BoltAPI instance."""

    # ── GET /apis/courses/featured — featured courses ──
    @bolt.get("/courses/featured")
    def list_featured_courses(request):
        """GET /apis/courses/featured — Featured courses (is_featured flag)."""
        from www.content.models.course import Course

        # Try is_featured filter first (DRF-compatible), fall back to -enrolled_count
        qs = Course.objects.filter(is_published=True)
        if hasattr(Course, "is_featured"):
            qs = qs.filter(is_featured=True)
        qs = qs.order_by("-enrolled_count")[:6]
        results = [_serialize_course_compact(c) for c in qs]
        return {"status": "success", "count": len(results), "results": results}

    # ── GET /apis/courses/<pk>/detail — extended detail ──
    # (Note: the existing GET /apis/courses/<pk> provides basic detail;
    #  this new endpoint returns full curriculum, objectives, etc.)

    @bolt.get("/courses/<int:pk>/detail")
    def get_course_detail(request, pk):
        """GET /apis/courses/<pk>/detail — Full course detail with curriculum."""
        from www.content.models.course import Course

        try:
            course = Course.objects.get(pk=pk, is_published=True)
        except Course.DoesNotExist:
            return {"status": "error", "message": "Course not found"}, 404

        return {"status": "success", "data": _serialize_course_full(course)}

    # ── GET /apis/courses/categories — already exists in apis.py ──
    # (not duplicated here)


def _serialize_course_compact(course) -> dict:
    """Compact serialization for listing (matches DRF CourseListSerializer)."""
    return {
        "id": course.pk,
        "title": course.title,
        "slug": getattr(course, "slug", ""),
        "short_description": getattr(course, "short_description", ""),
        "description": getattr(course, "description", ""),
        "price": float(getattr(course, "price", 0)),
        "discounted_price": None,
        "thumbnail": _course_image_url(course),
        "category": course.category.name if hasattr(course, "category") and course.category else "",
        "category_id": course.category_id,
        "instructor": getattr(course, "instructor", ""),
        "instructor_name": getattr(course, "instructor", ""),
        "duration": getattr(course, "duration", ""),
        "level": getattr(course, "skill_level", "beginner"),
        "language": getattr(course, "language", "English"),
        "students_count": getattr(course, "enrolled_count", 0),
        "rating": float(getattr(course, "rating", 0)),
        "reviews_count": 0,
        "is_featured": getattr(course, "is_featured", False),
        "has_certificate": True,
        "created_at": course.created_at.isoformat() if course.created_at else None,
    }


def _serialize_course_full(course) -> dict:
    """Full serialization with curriculum, objectives, requirements."""
    base = _serialize_course_compact(course)

    # Parse objectives, requirements, target_audience from text fields
    objectives = _parse_multiline(getattr(course, "objectives", ""))
    requirements = _parse_multiline(getattr(course, "requirements", ""))
    target_audience = _parse_multiline(getattr(course, "target_audience", ""))

    # Build curriculum (modules → lessons)
    curriculum = _build_curriculum(course)

    return {
        **base,
        "objectives": objectives,
        "requirements": requirements,
        "target_audience": target_audience,
        "curriculum": curriculum,
        "total_lessons": sum(m["lessons_count"] for m in curriculum),
    }


def _course_image_url(course) -> str:
    """Get image URL from a Course — try multiple field names."""
    for field in ("image", "thumbnail", "featured_image"):
        val = getattr(course, field, None)
        if val:
            url = get_image_url(val)
            if url:
                return url
    return ""


def _parse_multiline(text: str) -> list[str]:
    """Split a multiline text into a list of non-empty, stripped lines."""
    if not text:
        return []
    return [line.strip() for line in text.split("\n") if line.strip()]


def _build_curriculum(course) -> list[dict]:
    """Build curriculum structure: modules with their lessons."""
    modules = getattr(course, "modules", None)
    if modules is None:
        # Try reverse relation
        try:
            from plugins.lms.models.courses.detail import Module
            modules = Module.objects.filter(course=course).order_by("order")
        except Exception:
            return []

    curriculum = []
    for mod in modules.all().order_by("order"):
        lessons_list = []
        lessons = getattr(mod, "lessons", None)
        if lessons is not None:
            for lesson in lessons.all().order_by("order"):
                lessons_list.append({
                    "id": lesson.pk,
                    "title": lesson.title,
                    "description": getattr(lesson, "description", ""),
                    "video_url": getattr(lesson, "video_url", ""),
                    "duration": getattr(lesson, "duration", ""),
                    "order": getattr(lesson, "order", 0),
                    "is_preview": getattr(lesson, "is_preview", False),
                })

        curriculum.append({
            "id": mod.pk,
            "title": mod.title,
            "description": getattr(mod, "description", ""),
            "order": getattr(mod, "order", 0),
            "lessons": lessons_list,
            "lessons_count": len(lessons_list),
        })

    return curriculum
