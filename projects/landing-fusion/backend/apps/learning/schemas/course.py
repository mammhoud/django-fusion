from __future__ import annotations

from apps.learning.models import Course
from apps.learning.schemas.review import review_to_dict


def _lines(value) -> list[str]:
    """Newline-delimited model content as clean strings."""
    return [line.strip() for line in str(value or "").splitlines() if line.strip()]


def course_to_dict(course: Course) -> dict:
    """Public JSON shape for a course (course search API + ajax payloads)."""
    return {
        "slug": course.slug,
        "title": course.title,
        "short_description": course.short_description,
        "description": str(course.description),
        "objectives": course.objectives,
        "requirements": course.requirements,
        "target_audience": course.target_audience,
        "difficulty": course.difficulty,
        "language": course.language,
        "price": str(course.price),
        "duration_hours": str(course.duration_hours),
        "instructor": (
            {
                "name": (
                    f"{course.instructor.first_name} {course.instructor.last_name}".strip()
                    or course.instructor.username
                ),
            }
            if course.instructor_id
            else None
        ),
        "specializations": list(
            course.specializations.filter(is_active=True).values_list("title", flat=True)
        ),
        "tags": list(course.tags.values_list("name", flat=True)),
        "module_count": course.module_count,
        "lesson_count": course.lesson_count,
        "has_certificate": course.has_certificate,
        "is_free": course.is_free,
        "url": course.get_absolute_url(),
    }


def _lesson_to_dict(lesson) -> dict:
    """JSON shape for a lesson within a course detail payload."""
    return {
        "id": lesson.pk,
        "title": lesson.title,
        "description": lesson.description,
        "duration_minutes": lesson.duration_minutes,
        "is_preview": lesson.is_preview,
        "is_active": lesson.is_active,
        "resources": [
            {
                "id": resource.pk,
                "title": resource.title,
                "description": resource.description,
                "resource_type": resource.resource_type,
                "is_free": resource.is_free,
                "file_url": resource.file.url if resource.file else None,
            }
            for resource in lesson.resources.all().order_by("sort_order", "pk")
        ],
    }


def _module_to_dict(module) -> dict:
    """JSON shape for a module within a course detail payload."""
    return {
        "id": module.pk,
        "title": module.title,
        "description": module.description,
        "order": module.order,
        "lessons": [_lesson_to_dict(lesson) for lesson in module.lessons.all()],
    }


def course_detail_to_dict(course: Course) -> dict:
    """Full course detail payload — modules tree, resources, reviews (Precis parity).

    Mirrors Precis ``apps/learning/api/courses.py::course_detail`` so public
    consumers receive the same shape from the LF ``/learning/api/courses/<slug>/``
    endpoint.
    """
    return {
        "id": course.pk,
        "slug": course.slug,
        "title": course.title,
        "short_description": course.short_description,
        "description": str(course.description),
        "objectives": _lines(course.objectives),
        "requirements": _lines(course.requirements),
        "target_audience": _lines(course.target_audience),
        "specializations": list(
            course.specializations.filter(is_active=True).values_list("title", flat=True)
        ),
        "tags": list(course.tags.values_list("name", flat=True)),
        "instructor": (
            {
                "name": (
                    f"{course.instructor.first_name} {course.instructor.last_name}".strip()
                    or course.instructor.username
                ),
            }
            if course.instructor_id
            else None
        ),
        "difficulty": course.difficulty,
        "language": course.language,
        "duration_hours": str(course.duration_hours),
        "price": str(course.price),
        "is_free": course.is_free,
        "image_url": course.image_url,
        "rating": course.average_rating,
        "reviews_count": course.reviews_count,
        "enrollment_count": course.enrolled_count,
        "is_featured": course.is_featured,
        "has_certificate": course.has_certificate,
        "url": course.get_absolute_url(),
        "modules": [_module_to_dict(module) for module in course.modules.all()],
        "reviews": [
            review_to_dict(review)
            for review in course.reviews.published().select_related("user")[:20]
        ],
    }
