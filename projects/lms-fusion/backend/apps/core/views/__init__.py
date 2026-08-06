"""Views for LMS Fusion application."""
from .courses import (
    course_catalog,
    course_search,
    course_filter,
    course_detail,
    course_enrollment_form,
    course_enrollment_create,
    course_wishlist_toggle,
)

__all__ = [
    "course_catalog",
    "course_search",
    "course_filter",
    "course_detail",
    "course_enrollment_form",
    "course_enrollment_create",
    "course_wishlist_toggle",
]
