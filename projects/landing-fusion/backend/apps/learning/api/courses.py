from __future__ import annotations

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from apps.learning.management.services.courses import CourseService
from apps.learning.schemas.course import course_detail_to_dict, course_to_dict


@require_GET
def course_search_api(request):
    """Public course search — ``GET /learning/api/courses/search/?q=...``."""
    query = request.GET.get("q", "").strip()
    limit = min(int(request.GET.get("limit", 20)), 50)
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
    course = (
        CourseService.course_detail_queryset().filter(slug=slug).first()
    )
    if course is None:
        return JsonResponse(
            {"status": "error", "message": "Course not found"}, status=404
        )
    return JsonResponse(course_detail_to_dict(course))
