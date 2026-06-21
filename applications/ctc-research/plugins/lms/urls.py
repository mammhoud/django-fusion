from django.urls import path

# Import specific views without importing cart.py which depends on crafts_ai.rseal.site
from .views.courses import (
    FrontCourseDetailView,
    CourseSearchAPIView,
    course_wishlist_toggle,
    course_enrollment_form,
    course_enrollment_create,
)
from .views.lessons import (
    CourseWatchView,
    CourseContinueView,
    LessonNavigationView,
)
from .views.enrollment import (
    EnrollmentCreateAjaxView,
    enrollment_create_modal,
    enrollment_list,
    enrollment_status_update,
    enrollment_export_csv,
    enrollment_import_csv,
)
from .views.payments import (
    initialize_payment,
    verify_payment,
    payment_status,
    webhook_stripe,
    webhook_paypal,
    webhook_paymo,
)
from .views.cart import PaymentHistoryView
from .views.cart import EnrollView


# Lazy load crafts_ai.rseal payment views to avoid import conflicts
def _get_payment_urls():
    try:
        from crafts_ai.rseal.site.payments import (
            CartPayPalInitView,
            CartStripeInitView,
            PayPalInitView,
            StripeInitView,
            StripeWebhookView,
        )

        return [
            path("checkout/stripe/init/<slug:slug>/", StripeInitView.as_view(), name="stripe_init"),
            path("checkout/paypal/init/<slug:slug>/", PayPalInitView.as_view(), name="paypal_init"),
            path("checkout/stripe/init/", CartStripeInitView.as_view(), name="cart_stripe_init"),
            path("checkout/paypal/init/", CartPayPalInitView.as_view(), name="cart_paypal_init"),
            path("checkout/webhook/stripe/", StripeWebhookView.as_view(), name="stripe_webhook"),
        ]
    except (ImportError, RuntimeError):
        return []


app_name = "lms"

# =========================================================================
# URL PATTERNS FOR LMS (Learning Management System)
# =========================================================================
# Prefix: /learning/ (set in plugins/urls.py)
#
# ARCHITECTURE:
# - CoursesPage (Wagtail) handles catalog, listing, pagination via template
# - Django views provide API/AJAX endpoints for enrollment, wishlist, search
# - No HTMX duplicate views - all catalog logic in Wagtail templates
# =========================================================================

urlpatterns = [
    # ===================================================================
    # Course Detail & Learning
    # ===================================================================
    path("course/<slug:slug>/", FrontCourseDetailView.as_view(), name="course_view"),
    path(
        "course/<slug:slug>/lesson/<int:lesson_id>/", CourseWatchView.as_view(), name="course_watch"
    ),
    path("course/<slug:slug>/continue/", CourseContinueView.as_view(), name="course_continue"),
    path(
        "lesson/<int:lesson_id>/navigate/", LessonNavigationView.as_view(), name="lesson_navigate"
    ),
    # ===================================================================
    # Enrollment Management
    # ===================================================================
    path("enroll/<slug:slug>/", EnrollView.as_view(), name="enroll_course"),
    path("enrollment/success/", EnrollView.as_view(), name="enrollment_success"),
    path("enrollment/form/<int:course_id>/", course_enrollment_form, name="course_enrollment_form"),
    # AJAX Endpoints (v6 additions)
    path(
        "enrollment/create/ajax/<int:course_id>/",
        EnrollmentCreateAjaxView.as_view(),
        name="enrollment_create_ajax",
    ),
    path("enrollment/modal/<int:course_id>/", enrollment_create_modal, name="enrollment_modal"),
    path("enrollment/list/", enrollment_list, name="enrollment_list"),
    path(
        "enrollment/<int:enrollment_id>/status/",
        enrollment_status_update,
        name="enrollment_status_update",
    ),
    path("enrollment/export/csv/", enrollment_export_csv, name="enrollment_export_csv"),
    path("enrollment/import/csv/", enrollment_import_csv, name="enrollment_import_csv"),
    path(
        "enrollment/create/<int:course_id>/",
        course_enrollment_create,
        name="course_enrollment_create",
    ),
    path("dashboard/payments/", PaymentHistoryView.as_view(), name="payment_history"),
    # ===================================================================
    # Wishlist & User Actions
    # ===================================================================
    path("wishlist/toggle/<int:course_id>/", course_wishlist_toggle, name="course_wishlist_toggle"),
    # ===================================================================
    # API Endpoints
    # ===================================================================
    path("api/courses/search/", CourseSearchAPIView.as_view(), name="course_search_api"),
    # ===================================================================
    # Payment Providers (Phase 7)
    # ===================================================================
    path("payment/initialize/<int:enrollment_id>/", initialize_payment, name="payment_initialize"),
    path("payment/verify/<int:transaction_id>/", verify_payment, name="payment_verify"),
    path("payment/status/<int:transaction_id>/", payment_status, name="payment_status"),
    path("payment/webhook/stripe/", webhook_stripe, name="webhook_stripe"),
    path("payment/webhook/paypal/", webhook_paypal, name="webhook_paypal"),
    path("payment/webhook/paymo/", webhook_paymo, name="webhook_paymo"),
] + _get_payment_urls()
