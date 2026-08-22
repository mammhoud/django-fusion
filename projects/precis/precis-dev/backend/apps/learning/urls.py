from django.urls import path

from apps.learning import views
from apps.learning.api import courses as courses_api

app_name = "learning"

urlpatterns = [
    # ── Learner surface ────────────────────────────────────────────────
    path("", views.catalog, name="catalog"),
    path("course/<slug:slug>/", views.course_detail, name="course"),
    path("course/<slug:slug>/watch/", views.course_watch, name="course_watch"),
    path(
        "course/<slug:slug>/lesson/<int:lesson_id>/",
        views.course_watch,
        name="course_watch_lesson",
    ),
    path("course/<slug:slug>/continue/", views.course_continue, name="course_continue"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_dashboard, name="profile"),
    # ── Lesson actions ─────────────────────────────────────────────────
    path("lesson/<int:lesson_id>/complete/", views.complete_lesson, name="complete_lesson"),
    path("lesson/<int:lesson_id>/navigate/", views.lesson_navigate, name="lesson_navigate"),
    # ── Enrollment ─────────────────────────────────────────────────────
    path("course/<slug:slug>/enroll/", views.enroll, name="enroll"),
    path("enrollment/list/", views.enrollment_list, name="enrollment_list"),
    path(
        "enrollment/<int:enrollment_id>/status/",
        views.enrollment_status_update,
        name="enrollment_status_update",
    ),
    path(
        "enrollment/form/<int:course_id>/",
        views.course_enrollment_form,
        name="course_enrollment_form",
    ),
    # ── Wishlist ───────────────────────────────────────────────────────
    path("course/<slug:slug>/wishlist/", views.toggle_wishlist, name="wishlist"),
    # ── Public API ─────────────────────────────────────────────────────
    path("api/courses/search/", courses_api.course_search_api, name="course_search_api"),
    path("api/courses/<slug:slug>/", courses_api.course_detail_api, name="course_detail_api"),
]
