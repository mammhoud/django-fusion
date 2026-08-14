"""Django REST views for Fusion LMS courses API.

Mirrors the bolt API endpoints in bolt_apis.py but uses standard
Django function-based views so endpoints work with runserver (not just runbolt).

Mount: /api/courses, /api/courses/<slug>, /api/courses/filters
"""

from __future__ import annotations

import logging
from collections.abc import Mapping

from django.http import JsonResponse

logger = logging.getLogger(__name__)


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


def _media_urls(value) -> list[str]:
    """Extract URL-like values from a Wagtail media StreamField."""
    urls: list[str] = []

    def visit(item):
        if isinstance(item, str):
            if item.startswith(("http://", "https://", "/")):
                urls.append(item)
            return
        if isinstance(item, Mapping):
            for key in ("url", "embed_url", "src", "value"):
                if key in item:
                    visit(item[key])
            return
        if isinstance(item, (list, tuple)):
            for child in item:
                visit(child)

    visit(_json_value(value))
    return list(dict.fromkeys(urls))


def list_courses(request):
    """GET /api/courses — Course catalog with search, filters, pagination."""
    try:
        from django.db import models

        from apps.learning.models import Course

        qs = Course.objects.filter(is_published=True, is_active=True).order_by(
            "-is_featured", "-created_at"
        )

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
            qs = qs.filter(difficulty_level=diff)
        featured = _qp(request, "featured")
        if featured == "true":
            qs = qs.filter(is_featured=True)

        page = _qp_int(request, "page", 1)
        per_page = _qp_int(request, "per_page", 12)
        total = qs.count()
        courses = qs[(page - 1) * per_page : page * per_page]

        return JsonResponse({
            "data": [
                {
                    "id": c.pk, "title": c.title, "slug": c.slug,
                    "short_description": getattr(c, "short_description", ""),
                    "image_url": c.image.file.url if getattr(c, "image", None) else None,
                    "instructor": c.instructor.get_full_name() if getattr(c, "instructor", None) else "",
                    "price": float(getattr(c, "current_price", 0)),
                    "original_price": float(getattr(c, "original_price", 0)) if getattr(c, "original_price", 0) else None,
                    "currency": getattr(c, "currency", "") or "USD",
                    "difficulty": getattr(c, "difficulty_level", ""),
                    "language": getattr(c, "language", ""),
                    "duration": getattr(c, "duration", 0),
                    "rating": float(getattr(c, "average_rating", 0)),
                    "reviews_count": getattr(c, "reviews_count", 0),
                    "is_featured": getattr(c, "is_featured", False),
                    "has_certificate": getattr(c, "has_certificate", False),
                }
                for c in courses
            ],
            "pagination": {
                "page": page, "per_page": per_page, "total": total,
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

        course = Course.objects.filter(slug=slug, is_published=True, is_active=True).first()
        if course is None:
            return JsonResponse({"status": "error", "message": "Course not found"}, status=404)

        modules_data = []
        try:
            for mod in course.modules.filter(is_published=True).order_by("order"):
                lessons = [
                    {
                        "id": ln.pk, "title": ln.title,
                        "is_preview": getattr(ln, "is_preview", False),
                        "duration": getattr(ln, "duration", 0),
                    }
                    for ln in mod.lessons.filter(is_published=True).order_by("order")
                ]
                modules_data.append({
                    "id": mod.pk, "title": mod.title,
                    "description": getattr(mod, "description", ""),
                    "lessons": lessons,
                })
        except Exception:
            pass

        instructor = getattr(course, "instructor", None)
        instructor_profile = getattr(instructor, "profile", None) if instructor else None

        # Person (user.profile) — fields are nullable, so emit nulls when empty.
        profile_data = None
        if instructor_profile:
            profile_data = {
                "avatar": instructor_profile.profile_image.url if instructor_profile.profile_image else None,
                "title": instructor_profile.job_title or "",
                "bio": instructor_profile.bio or "",
                "website": instructor_profile.website or None,
                "linkedin": instructor_profile.linkedin_url or None,
            }

        return JsonResponse({
            "id": course.pk, "title": course.title, "slug": course.slug,
            "description": _json_value(getattr(course, "description", "")),
            "short_description": getattr(course, "short_description", ""),
            "overview": _json_value(getattr(course, "overview", "")),
            "image_url": course.image.file.url if getattr(course, "image", None) else None,
            "header_image": course.header_image.file.url if getattr(course, "header_image", None) else None,
            "preview_video_url": _media_urls(getattr(course, "preview_video", "")),
            "objectives": _lines(getattr(course, "objectives", "")),
            "requirements": _lines(getattr(course, "requirements", "")),
            "target_audience": _lines(getattr(course, "target_audience", "")),
            "specializations": list(course.specializations.values_list("title", flat=True)),
            "tags": list(course.tags.values_list("name", flat=True)),
            "instructor": {
                "name": instructor.get_full_name() if instructor else "",
                "username": getattr(instructor, "username", "") if instructor else "",
                "bio": _json_value(getattr(instructor, "bio", "")) if instructor else "",
                "profile": profile_data,
            },
            "price": float(getattr(course, "current_price", 0)),
            "current_price": float(getattr(course, "current_price", 0)),
            "original_price": float(getattr(course, "original_price", 0)) if getattr(course, "original_price", 0) else None,
            "currency": getattr(course, "currency", "") or "USD",
            "discount_percentage": float(getattr(course, "discount_percentage", 0)),
            "discount_percentage_calculated": float(getattr(course, "discount_percentage_calculated", 0)),
            "discount_until": str(course.discount_until) if getattr(course, "discount_until", None) else None,
            "is_free": bool(getattr(course, "is_free", False)),
            "is_discounted": bool(getattr(course, "is_discounted", False)),
            "difficulty": getattr(course, "difficulty_level", ""),
            "language": getattr(course, "language", ""),
            "duration": getattr(course, "duration", 0),
            "rating": float(getattr(course, "average_rating", 0)),
            "average_rating": float(getattr(course, "average_rating", 0)),
            "reviews_count": getattr(course, "reviews_count", 0),
            "enrollment_count": getattr(course, "enrolled_count", 0),
            "enrolled_count": getattr(course, "enrolled_count", 0),
            "is_featured": getattr(course, "is_featured", False),
            "has_certificate": getattr(course, "has_certificate", False),
            "modules": modules_data,
        })
    except Exception:
        logger.exception("Error loading course detail")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)


def course_filters(request):
    """GET /api/courses/filters — Available filter options for the course catalog."""
    try:
        from apps.learning.models import Course

        languages = list(
            Course.objects.filter(is_published=True, is_active=True)
            .values_list("language", flat=True).distinct().order_by("language")
        )
        difficulties = list(
            Course.objects.filter(is_published=True, is_active=True)
            .values_list("difficulty_level", flat=True).distinct()
        )

        return JsonResponse({
            "languages": [code for code in languages if code],
            "difficulties": [level for level in difficulties if level],
        })
    except Exception:
        return JsonResponse({"languages": [], "difficulties": []})
