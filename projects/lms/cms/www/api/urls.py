"""
LMS REST API — URL configuration (bolt-pattern function views).

All endpoints are prefixed with /api/ in the root URL configuration.
Uses bolt-style function views via the @bolt_view adapter decorator.
"""

from django.urls import path

from . import auth, courses, students, instructors, blog, shop, events, contact

app_name = "api"

urlpatterns = [
    # ── Auth ──
    path("auth/login/", auth.login_view, name="auth_login"),
    path("auth/register/", auth.register_view, name="auth_register"),
    path("auth/logout/", auth.logout_view, name="auth_logout"),
    path("auth/profile/", auth.profile_view, name="auth_profile"),
    path("auth/password-reset/", auth.password_reset_view, name="auth_password_reset"),
    path("auth/change-password/", auth.change_password_view, name="auth_change_password"),

    # ── Courses ──
    path("courses/", courses.course_list, name="course_list"),
    path("courses/featured/", courses.featured_courses, name="course_featured"),
    path("courses/<pk>/", courses.course_detail, name="course_detail"),
    path("categories/", courses.category_list, name="category_list"),

    # ── Students ──
    path("students/dashboard/", students.student_dashboard, name="student_dashboard"),
    path("students/reviews/", students.student_reviews, name="student_reviews"),
    path("students/enrollments/<pk>/", students.student_enrollment_detail, name="student_enrollment_detail"),
    path("students/enroll/", students.enroll_in_course, name="student_enroll"),
    path("students/progress/", students.progress_update, name="student_progress"),
    path("students/<pk>/enrollments/", students.student_enrollments, name="student_enrollments"),

    # ── Instructors ──
    path("instructors/", instructors.instructor_list, name="instructor_list"),
    path("instructors/<pk>/", instructors.instructor_detail, name="instructor_detail"),
    path("instructors/<pk>/dashboard/", instructors.instructor_dashboard, name="instructor_dashboard"),
    path("instructors/<pk>/courses/", instructors.instructor_courses, name="instructor_courses"),
    path("instructors/<pk>/reviews/", instructors.instructor_reviews, name="instructor_reviews"),
    path("instructors/courses/<pk>/", instructors.instructor_delete_course, name="instructor_delete_course"),

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
    path("shop/orders/", shop.order_list, name="shop_order_list"),

    # ── Events ──
    path("events/", events.event_list, name="event_list"),
    path("events/<pk>/", events.event_detail, name="event_detail"),

    # ── Contact ──
    path("contact/", contact.contact_submit, name="contact_submit"),
]
