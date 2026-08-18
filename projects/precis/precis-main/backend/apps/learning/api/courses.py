"""Django REST views for the merged Precis course API.

Two contracts are served from the same ``apps.learning`` Course model:

* ``/learning/api/courses/...`` — the landing search + detail contract
  (``course_search_api`` / ``course_detail_api``), consumed by the Django
  road and the Astro data-API road.
* ``/api/courses/...`` — the LMS frontend catalog contract (``list_courses``,
  ``course_detail``, ``course_filters``) with pagination, consumed by the
  Astro ``courses/`` pages (``fetchCourseList*`` / ``fetchCourseDetail*``).

The LMS serializer is adapted to the landing Course model field names
(``difficulty`` → ``difficulty_level``, ``duration_hours`` → ``duration``,
``price`` → ``current_price``) while preserving the response shape the
frontend expects.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping

from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


# ── Landing contract ──────────────────────────────────────────────────────────

@require_GET
def course_search_api(request):
    """Public course search — ``GET /learning/api/courses/search/?q=...``."""
    query = request.GET.get("q", "").strip()
    limit = min(int(request.GET.get("limit", 20)), 50)
    from apps.learning.management.services.courses import CourseService
    from apps.learning.schemas.course import course_to_dict

    courses = CourseService.search(query)[:limit]
    results = [course_to_dict(course) for course in courses]
    return JsonResponse(
        {
            "results": results,
            "count": len(results),
            "query": query,
        }
    )


@require_GET
def course_detail_api(request, slug):
    """Public course detail — ``GET /learning/api/courses/<slug>/`` (Precis parity)."""
    from apps.learning.management.services.courses import CourseService
    from apps.learning.schemas.course import course_detail_to_dict

    course = (
        CourseService.course_detail_queryset().filter(slug=slug).first()
    )
    if course is None:
        return JsonResponse(
            {"status": "error", "message": "Course not found"}, status=404
        )
    return JsonResponse(course_detail_to_dict(course))


# ── LMS catalog contract (/api/courses/) ──────────────────────────────────────

def _json_value(value):
    """Convert Wagtail values into JSON-safe data without rendering templates."""
    if value is None:
        return ""
    if hasattr(value, "stream_block"):
        return [
            {
                "type": block.block_type,
                "value": _json_value(block.value),
            }
            for block in value
        ]
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _qp(request, key: str, default: str = "") -> str:
    """Get a query parameter safely."""
    return request.GET.get(key, default)


def _qp_int(request, key: str, default: int = 1) -> int:
    """Get an integer query parameter safely."""
    try:
        return int(_qp(request, key, str(default)))
    except (TypeError, ValueError):
        return default


def _lines(value) -> list[str]:
    """Return newline-delimited model content as clean JSON strings."""
    return [line.strip() for line in str(value or "").splitlines() if line.strip()]


def _course_base_dict(course) -> dict:
    """Shared card fields for the LMS catalog contract (landing model)."""
    from django.conf import settings

    currency = str(getattr(settings, "FUSION_DEFAULT_CURRENCY", "USD") or "USD")
    difficulty = course.get_difficulty_display() if hasattr(course, "get_difficulty_display") else ""
    return {
        "id": course.pk,
        "title": course.title,
        "slug": course.slug,
        "short_description": getattr(course, "short_description", ""),
        "image_url": course.image_url if hasattr(course, "image_url") else None,
        "instructor": course.instructor.get_full_name() if getattr(course, "instructor", None) else "",
        "price": float(getattr(course, "price", 0) or 0),
        "original_price": None,
        "currency": currency,
        "difficulty": difficulty,
        "language": getattr(course, "language", ""),
        "duration": float(getattr(course, "duration_hours", 0) or 0),
        "rating": float(getattr(course, "average_rating", 0) or 0),
        "reviews_count": getattr(course, "reviews_count", 0) or 0,
        "is_featured": getattr(course, "is_featured", False),
        "has_certificate": getattr(course, "has_certificate", False),
    }


def _course_detail_dict(course) -> dict:
    """Full detail payload for the LMS course page (landing model)."""
    data = _course_base_dict(course)

    modules_data = []
    try:
        for mod in course.modules.all().order_by("order"):
            lessons = [
                {
                    "id": ln.pk,
                    "title": ln.title,
                    "is_preview": getattr(ln, "is_preview", False),
                    "duration": getattr(ln, "duration_minutes", 0) or 0,
                }
                for ln in mod.lessons.filter(is_active=True).order_by("order")
            ]
            modules_data.append({
                "id": mod.pk,
                "title": mod.title,
                "description": getattr(mod, "description", ""),
                "lessons": lessons,
            })
    except Exception:  # pragma: no cover - defensive per-module serialization
        logger.exception("Course module serialization failed")

    instructor = getattr(course, "instructor", None)
    specializations = []
    tags = []
    try:
        specializations = list(course.specializations.values_list("title", flat=True))
    except Exception:
        pass
    try:
        tags = list(course.tags.values_list("name", flat=True))
    except Exception:
        pass

    data.update({
        "description": _json_value(getattr(course, "description", "")),
        "overview": _json_value(getattr(course, "description", "")),
        "header_image": course.image_url if hasattr(course, "image_url") else None,
        "preview_video_url": [],
        "objectives": _lines(getattr(course, "objectives", "")),
        "requirements": _lines(getattr(course, "requirements", "")),
        "target_audience": _lines(getattr(course, "target_audience", "")),
        "specializations": specializations,
        "tags": tags,
        "instructor": {
            "name": instructor.get_full_name() if instructor else "",
            "username": getattr(instructor, "username", "") if instructor else "",
            "bio": _json_value(getattr(instructor, "bio", "")) if instructor else "",
            "profile": None,
        },
        "current_price": float(getattr(course, "price", 0) or 0),
        "discount_percentage": 0,
        "discount_percentage_calculated": 0,
        "discount_until": None,
        "is_free": bool(getattr(course, "is_free", False)),
        "is_discounted": False,
        "enrollment_count": getattr(course, "enrolled_count", 0) or 0,
        "enrolled_count": getattr(course, "enrolled_count", 0) or 0,
        "modules": modules_data,
    })
    return data


def list_courses(request):
    """GET /api/courses — Course catalog with search, filters, pagination."""
    try:
        from django.db import models

        from apps.learning.models import Course

        qs = Course.objects.filter(is_published=True).order_by("-is_featured", "-created_at")

        q = _qp(request, "q")
        if q:
            qs = qs.filter(
                models.Q(title__icontains=q)
                | models.Q(short_description__icontains=q)
            )

        lang = _qp(request, "language")
        if lang:
            qs = qs.filter(language=lang)
        diff = _qp(request, "difficulty")
        if diff:
            qs = qs.filter(difficulty=diff)
        featured = _qp(request, "featured")
        if featured == "true":
            qs = qs.filter(is_featured=True)

        page = _qp_int(request, "page", 1)
        per_page = _qp_int(request, "per_page", 12)
        total = qs.count()
        courses = qs[(page - 1) * per_page : page * per_page]

        return JsonResponse({
            "data": [_course_base_dict(course) for course in courses],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
        })
    except Exception:
        logger.exception("Error listing courses")
        return JsonResponse(
            {"status": "error", "message": "Unable to load course catalog"},
            status=500,
        )


def course_detail(request, slug):
    """GET /api/courses/<slug> — Single course detail with modules."""
    try:
        from apps.learning.models import Course

        course = Course.objects.filter(slug=slug, is_published=True).first()
        if course is None:
            return JsonResponse({"status": "error", "message": "Course not found"}, status=404)
        return JsonResponse(_course_detail_dict(course))
    except Exception:
        logger.exception("Error loading course detail")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)


def course_filters(request):
    """GET /api/courses/filters — Available filter options for the course catalog."""
    try:
        from apps.learning.models import Course

        languages = list(
            Course.objects.filter(is_published=True)
            .values_list("language", flat=True).distinct().order_by("language")
        )
        difficulties = list(
            Course.objects.filter(is_published=True)
            .values_list("difficulty", flat=True).distinct()
        )
        return JsonResponse({
            "languages": [code for code in languages if code],
            "difficulties": [level for level in difficulties if level],
        })
    except Exception:
        return JsonResponse({"languages": [], "difficulties": []})
