"""Django REST views for Fusion LMS courses API.

Mirrors the bolt API endpoints in bolt_apis.py but uses standard
Django function-based views so endpoints work with runserver (not just runbolt).

Mount: /api/courses, /api/courses/<slug>, /api/courses/filters
"""

from __future__ import annotations

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def _qp(request, key: str, default: str = "") -> str:
    """Get a query parameter safely."""
    return request.GET.get(key, default)


def _qp_int(request, key: str, default: int = 1) -> int:
    """Get an integer query parameter safely."""
    try:
        return int(_qp(request, key, str(default)))
    except (TypeError, ValueError):
        return default


def list_courses(request):
    """GET /api/courses — Course catalog with search, filters, pagination."""
    try:
        from django.db import models
        from plugins.lms.models import Course

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
            {"data": [], "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0}}
        )


def course_detail(request, slug):
    """GET /api/courses/<slug> — Single course detail with modules."""
    try:
        from plugins.lms.models import Course

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

        return JsonResponse({
            "id": course.pk, "title": course.title, "slug": course.slug,
            "description": getattr(course, "description", ""),
            "short_description": getattr(course, "short_description", ""),
            "overview": getattr(course, "overview", ""),
            "image_url": course.image.file.url if getattr(course, "image", None) else None,
            "preview_video_url": getattr(course, "preview_video", ""),
            "instructor": {
                "name": course.instructor.get_full_name() if getattr(course, "instructor", None) else "",
                "bio": getattr(course.instructor, "bio", "") if getattr(course, "instructor", None) else "",
            },
            "price": float(getattr(course, "current_price", 0)),
            "original_price": float(getattr(course, "original_price", 0)) if getattr(course, "original_price", 0) else None,
            "discount_percentage": float(getattr(course, "discount_percentage", 0)),
            "difficulty": getattr(course, "difficulty_level", ""),
            "language": getattr(course, "language", ""),
            "duration": getattr(course, "duration", 0),
            "rating": float(getattr(course, "average_rating", 0)),
            "reviews_count": getattr(course, "reviews_count", 0),
            "enrollment_count": getattr(course, "enrollment_count", 0),
            "is_featured": getattr(course, "is_featured", False),
            "has_certificate": getattr(course, "has_certificate", False),
            "modules": modules_data,
            "requirements": list(getattr(course, "requirements", "").split("\n")) if getattr(course, "requirements", "") else [],
        })
    except Exception:
        logger.exception("Error loading course detail")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)


def course_filters(request):
    """GET /api/courses/filters — Available filter options for the course catalog."""
    try:
        from plugins.lms.models import Course

        languages = list(
            Course.objects.filter(is_published=True, is_active=True)
            .values_list("language", flat=True).distinct().order_by("language")
        )
        difficulties = list(
            Course.objects.filter(is_published=True, is_active=True)
            .values_list("difficulty_level", flat=True).distinct()
        )

        return JsonResponse({
            "languages": [l for l in languages if l],
            "difficulties": [d for d in difficulties if d],
        })
    except Exception:
        return JsonResponse({"languages": [], "difficulties": []})
