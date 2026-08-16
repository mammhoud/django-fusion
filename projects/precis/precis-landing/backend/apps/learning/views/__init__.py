"""Learning views — split by domain, mirroring the Precis learning app.

The flat ``views.py`` was split into this package. Everything is re-exported
here so existing imports (``from apps.learning.views import catalog`` and
``from apps.learning import views``) keep resolving unchanged.
"""
from .common import (
    _hx_or_json,
    _is_htmx,
    _login_response,
    learning_login_required,
)
from .courses import catalog, course_detail
from .enrollment import (
    course_enrollment_form,
    enroll,
    enrollment_list,
    enrollment_status_update,
)
from .lessons import complete_lesson, course_continue, course_watch, lesson_navigate
from .profile import dashboard, profile_dashboard
from .wishlist import toggle_wishlist

__all__ = [
    # helpers
    "_hx_or_json",
    "_is_htmx",
    "_login_response",
    "learning_login_required",
    # courses
    "catalog",
    "course_detail",
    # lessons
    "complete_lesson",
    "course_continue",
    "course_watch",
    "lesson_navigate",
    # enrollment
    "course_enrollment_form",
    "enroll",
    "enrollment_list",
    "enrollment_status_update",
    # profile
    "dashboard",
    "profile_dashboard",
    # wishlist
    "toggle_wishlist",
]
