"""
LMS REST API — URL configuration (bolt-pattern function views).

All endpoints are prefixed with /api/ in the root URL configuration.
Uses bolt-style function views via the @bolt_view adapter decorator.
"""

from django.urls import path

from . import auth, courses, students, instructors, blog, shop, events, contact, pages, i18n, fusion_health
from . import notifications
from . import announcements
from . import assignments
from . import quiz as quiz_views
from plugins.lms.views import video as video_views

app_name = "api"

urlpatterns = [
    # ── Auth ──
    path("auth/login/", auth.login_view, name="auth_login"),
    path("auth/register/", auth.register_view, name="auth_register"),
    path("auth/logout/", auth.logout_view, name="auth_logout"),
    path("auth/profile/", auth.profile_view, name="auth_profile"),
    path("auth/password-reset/", auth.password_reset_view, name="auth_password_reset"),
    path(
        "auth/change-password/", auth.change_password_view, name="auth_change_password"
    ),
    # ── Courses ──
    path("courses/", courses.course_list, name="course_list"),
    path("courses/featured/", courses.featured_courses, name="course_featured"),
    path("courses/<pk>/", courses.course_detail, name="course_detail"),
    path("categories/", courses.category_list, name="category_list"),
    # ── Students ──
    path("students/dashboard/", students.student_dashboard, name="student_dashboard"),
    path("students/reviews/", students.student_reviews, name="student_reviews"),
    path(
        "students/enrollments/<pk>/",
        students.student_enrollment_detail,
        name="student_enrollment_detail",
    ),
    path("students/enroll/", students.enroll_in_course, name="student_enroll"),
    path("students/progress/", students.progress_update, name="student_progress"),
    path(
        "students/<pk>/enrollments/",
        students.student_enrollments,
        name="student_enrollments",
    ),
    # ── Instructors ──
    path("instructors/", instructors.instructor_list, name="instructor_list"),
    path(
        "instructors/me/dashboard/",
        instructors.instructor_dashboard_me,
        name="instructor_dashboard_me",
    ),
    path("instructors/<pk>/", instructors.instructor_detail, name="instructor_detail"),
    path(
        "instructors/<pk>/dashboard/",
        instructors.instructor_dashboard,
        name="instructor_dashboard",
    ),
    path(
        "instructors/<pk>/courses/",
        instructors.instructor_courses,
        name="instructor_courses",
    ),
    path(
        "instructors/<pk>/reviews/",
        instructors.instructor_reviews,
        name="instructor_reviews",
    ),
    path(
        "instructors/courses/<pk>/",
        instructors.instructor_delete_course,
        name="instructor_delete_course",
    ),
    # ── Blog ──
    path("blog/posts/", blog.blog_post_list, name="blog_post_list"),
    path("blog/posts/featured/", blog.featured_posts, name="blog_post_featured"),
    path("blog/posts/<pk>/", blog.blog_post_detail, name="blog_post_detail"),
    path("blog/categories/", blog.blog_category_list, name="blog_category_list"),
    # ── Shop ──
    path("shop/products/", shop.product_list, name="shop_product_list"),
    path("shop/products/<pk>/", shop.product_detail, name="shop_product_detail"),
    path("shop/cart/", shop.cart_view, name="shop_cart"),
    path("shop/cart/add/", shop.cart_add, name="shop_cart_add"),
    path("shop/cart/<item_id>/", shop.cart_item_view, name="shop_cart_item"),
    path("shop/orders/", shop.orders_view, name="shop_orders"),

#     path("shop/orders/", shop.order_list, name="shop_order_list"),
    # ── Events ──
    path("events/", events.event_list, name="event_list"),
    path("events/<pk>/", events.event_detail, name="event_detail"),
    # ── Pages ──
    path("fusion/health", fusion_health.fusion_health, name="fusion_health"),
    path("pages/<slug:slug>/", pages.page_detail, name="page_detail"),
    path(
        "pages/<slug:slug>/fragment/",
        pages.page_fragment,
        name="page_fragment",
    ),
    path(
        "pages/<slug:slug>/data/",
        pages.page_data,
        name="page_data",
    ),
    # ── i18n ──
    path("i18n/setlang/", i18n.set_language_view, name="i18n_setlang"),
    path("i18n/languages/", i18n.language_list, name="i18n_language_list"),
    # ── Dashboard Content ──
    path("dashboard/content/", dashboard_content.dashboard_content, name="dashboard_content"),
    # ── Videos ──
    path("videos/lesson/<int:lesson_id>/", video_views.video_list, name="api_video_list"),
    path("videos/<int:video_id>/", video_views.video_detail, name="api_video_detail"),
    path("videos/upload/", video_views.video_upload, name="api_video_upload"),
    path("videos/<int:video_id>/delete/", video_views.video_delete, name="api_video_delete"),
    path("videos/<int:video_id>/processing-callback/", video_views.video_processing_callback, name="api_video_processing_callback"),
    # ── Notifications ──
    path("notifications/", notifications.notification_list, name="notification_list"),
    path(
        "notifications/unread-count/",
        notifications.notification_unread_count,
        name="notification_unread_count",
    ),
    path(
        "notifications/mark-all-read/",
        notifications.notification_mark_all_read,
        name="notification_mark_all_read",
    ),
    path(
        "notifications/<pk>/read/",
        notifications.notification_mark_read,
        name="notification_mark_read",
    ),
    path(
        "notifications/<pk>/",
        notifications.notification_dismiss,
        name="notification_dismiss",
    ),
    path(
        "notifications/preferences/",
        notifications.notification_preferences_get,
        name="notification_preferences_get",
    ),
    path(
        "notifications/preferences/update/",
        notifications.notification_preferences_update,
        name="notification_preferences_update",
    ),
    # ── Quiz ──
    path("quizzes/", quiz_views.quiz_list, name="quiz_list"),
    path("quizzes/create/", quiz_views.quiz_create, name="quiz_create"),
    path("quizzes/<pk>/", quiz_views.quiz_detail, name="quiz_detail"),
    path("quizzes/<pk>/update/", quiz_views.quiz_update, name="quiz_update"),
    path("quizzes/<pk>/delete/", quiz_views.quiz_delete, name="quiz_delete"),
    path(
        "quizzes/<quiz_pk>/questions/",
        quiz_views.question_create,
        name="question_create",
    ),
    path(
        "quizzes/questions/<pk>/update/",
        quiz_views.question_update,
        name="question_update",
    ),
    path(
        "quizzes/questions/<pk>/delete/",
        quiz_views.question_delete,
        name="question_delete",
    ),
    path(
        "quizzes/<quiz_pk>/attempts/start/",
        quiz_views.attempt_start,
        name="attempt_start",
    ),
    path(
        "quizzes/<quiz_pk>/attempts/",
        quiz_views.quiz_attempts,
        name="quiz_attempts",
    ),
    path("attempts/", quiz_views.attempt_list, name="attempt_list"),
    path("attempts/<pk>/", quiz_views.attempt_detail, name="attempt_detail"),
    path(
        "attempts/<pk>/submit/",
        quiz_views.attempt_submit,
        name="attempt_submit",
    ),
    path(
        "attempts/<pk>/grade/",
        quiz_views.attempt_grade,
        name="attempt_grade",
    ),
    # ── Assignments ──
    path("assignments/", assignments.assignment_list, name="assignment_list"),
    path("assignments/create/", assignments.assignment_create, name="assignment_create"),
    path("assignments/<pk>/", assignments.assignment_detail, name="assignment_detail"),
    path("assignments/<pk>/update/", assignments.assignment_update, name="assignment_update"),
    path("assignments/<pk>/delete/", assignments.assignment_delete, name="assignment_delete"),
    path("assignments/<pk>/submit/", assignments.assignment_submit, name="assignment_submit"),
    path("assignments/<pk>/submissions/", assignments.assignment_submissions, name="assignment_submissions"),
    path("submissions/", assignments.my_submissions, name="my_submissions"),
    path("submissions/<pk>/grade/", assignments.submission_grade, name="submission_grade"),
    # ── Announcements ──
    path("announcements/", announcements.announcement_list, name="announcement_list"),
    path("announcements/create/", announcements.announcement_create, name="announcement_create"),
    path("announcements/<pk>/", announcements.announcement_detail, name="announcement_detail"),
    path("announcements/<pk>/update/", announcements.announcement_update, name="announcement_update"),
    path("announcements/<pk>/delete/", announcements.announcement_delete, name="announcement_delete"),
    # ── Contact ──
    path("contact/", contact.contact_submit, name="contact_submit"),
]
