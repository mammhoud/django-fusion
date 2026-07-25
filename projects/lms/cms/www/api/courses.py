"""
Courses API — list, detail, featured, categories (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/courses.ts
"""

import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404

from plugins.lms.models import Course, CourseCategory
from www.api.data_adapter import (
    bolt_view,
    paginate_queryset,
    parse_body,
    get_image_url,
    get_user_display_name,
    paginated_response,
)

logger = logging.getLogger(__name__)


def _serialize_course(course: Course) -> dict:
    """Serialize a Course to the frontend-expected format."""
    try:
        instructor = course.instructor
        instructor_name = (
            f"{instructor.first_name} {instructor.last_name}".strip()
            or instructor.username
        )
    except Exception:
        instructor_name = ""
        instructor = None

    image_url = get_image_url(getattr(course, "image", None))

    categories = []
    try:
        categories = list(course.categories.values_list("title", flat=True))
    except Exception:
        pass

    return {
        "id": course.id,
        "title": course.title,
        "slug": course.slug,
        "short_description": course.short_description or "",
        "description": course.description or "",
        "image": image_url,
        "price": float(course.final_price),
        "original_price": (
            float(course.original_price) if course.original_price else None
        ),
        "instructor": course.instructor_id,
        "instructor_name": instructor_name,
        "instructor_avatar": "",
        "category_name": categories[0] if categories else "",
        "category_id": (
            course.categories.first().id if course.categories.exists() else None
        ),
        "categories": categories,
        "difficulty_level": course.difficulty_level,
        "language": course.language,
        "duration": course.duration,
        "total_lessons": course.total_lessons,
        "enrolled_count": course.enrolled_count,
        "rating": float(course.average_rating),
        "reviews_count": course.reviews_count,
        "is_published": course.is_published,
        "is_featured": course.is_featured,
        "has_certificate": course.has_certificate,
        "url": course.url,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None,
    }


def _serialize_category(category: CourseCategory) -> dict:
    """Serialize a CourseCategory."""
    return {
        "id": category.id,
        "name": category.title,
        "slug": category.slug,
        "description": category.description or "",
        "course_count": category.course_count,
    }


def _build_curriculum(course) -> list[dict]:
    """Build curriculum structure: modules with their lessons."""
    from plugins.lms.models import Video

    modules = []
    for mod in course.modules.all().order_by("order"):
        lessons = []
        for lesson in mod.lessons.all().order_by("order"):
            # Get the first ready video for this lesson
            primary_video = Video.objects.filter(
                lesson=lesson, is_active=True,
                processing_status=Video.ProcessingStatus.READY,
            ).order_by("sort_order", "created_at").first()

            lessons.append(
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "duration": lesson.duration,
                    "video_url": lesson.video_url or "",
                    "video_file_url": primary_video.streaming_url if primary_video else "",
                    "video_id": primary_video.pk if primary_video else None,
                    "has_video": primary_video is not None or bool(lesson.video_url),
                    "is_preview": lesson.is_preview,
                }
            )
        modules.append(
            {
                "id": mod.id,
                "title": mod.title,
                "description": mod.description or "",
                "order": mod.order,
                "lessons": lessons,
                "lessons_count": len(lessons),
            }
        )
    return modules


# ── Views ──


@bolt_view
def course_list(request):
    """GET /api/courses/ — List published courses with optional search/filter."""
    queryset = Course.objects.filter(is_published=True, is_active=True)

    q = request.GET.get("search", "").strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q)
            | Q(short_description__icontains=q)
            | Q(description__icontains=q)
        )

    category = request.GET.get("category", "").strip()
    if category:
        queryset = queryset.filter(categories__slug=category)

    level = request.GET.get("level", "").strip()
    if level:
        queryset = queryset.filter(difficulty_level=level)

    language = request.GET.get("language", "").strip()
    if language:
        queryset = queryset.filter(language=language)

    sort = request.GET.get("sorting", "-created_at")
    allowed_sorts = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_asc": "final_price",
        "price_desc": "-final_price",
        "popular": "-enrolled_count",
        "rating": "-average_rating",
    }
    queryset = queryset.order_by(allowed_sorts.get(sort, "-created_at"))

    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 12))
    items, pagination = paginate_queryset(queryset, request, page_size)

    return paginated_response(
        items, pagination, request, [_serialize_course(c) for c in items]
    )


@bolt_view
def course_detail(request, pk):
    """GET /api/courses/<pk>/ — Get full course details."""
    try:
        course = Course.objects.get(
            Q(pk=pk) | Q(slug=pk),
            is_published=True,
            is_active=True,
        )
    except Course.DoesNotExist:
        return {"status": "error", "message": "Course not found"}, 404

    data = _serialize_course(course)
    data["curriculum"] = _build_curriculum(course)
    data["objectives"] = (
        course.objectives_list if hasattr(course, "objectives_list") else []
    )
    data["requirements"] = (
        course.requirements_list if hasattr(course, "requirements_list") else []
    )

    return {"status": "success", "data": data}


@bolt_view
def featured_courses(request):
    """GET /api/courses/featured/ — Get featured/promoted courses."""
    courses = Course.objects.filter(
        is_published=True, is_active=True, is_featured=True
    )[:6]
    return {
        "results": [_serialize_course(c) for c in courses],
        "count": courses.count(),
        "next": None,
        "previous": None,
    }


@bolt_view
def category_list(request):
    """GET /api/categories/ — List all active course categories."""
    categories = CourseCategory.objects.filter(is_active=True).order_by(
        "order", "title"
    )
    return {
        "results": [_serialize_category(c) for c in categories],
        "count": categories.count(),
        "next": None,
        "previous": None,
    }
