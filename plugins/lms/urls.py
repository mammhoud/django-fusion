from django.urls import path

from .views import *

try:
    from django_rseal.workflows.pipelines.site.payments import (
        CartPayPalInitView,
        CartStripeInitView,
        PayPalInitView,
        StripeInitView,
        StripeWebhookView,
    )
    payment_urls = [
        path("checkout/stripe/init/<slug:slug>/", StripeInitView.as_view(), name="stripe_init"),
        path("checkout/paypal/init/<slug:slug>/", PayPalInitView.as_view(), name="paypal_init"),
        path("checkout/stripe/init/", CartStripeInitView.as_view(), name="cart_stripe_init"),
        path("checkout/paypal/init/", CartPayPalInitView.as_view(), name="cart_paypal_init"),
        path("checkout/webhook/stripe/", StripeWebhookView.as_view(), name="stripe_webhook"),
    ]
except ImportError:
    payment_urls = []

# from .search import views as search_views
# from www.core.commons.views import *
# from .api import api_router
# from .views import CourseSearchView

app_name = "lms"
urlpatterns = [
    path("course/<slug:slug>/", FrontCourseDetailView.as_view(), name="course"),
    # path("lessons/<slug:slug>/", FrontCourseLesson.as_view(), name="lessons"),
    # path("lessons/<slug:slug>/<int:pk>/", FrontLessons.as_view(), name="lesson"),
    path(
        "course/<slug:slug>/lesson/<int:lesson_id>/",
        CourseWatchView.as_view(),
        name="course_watch",
    ),
    path(
        "course/<slug:slug>/continue/",
        CourseContinueView.as_view(),
        name="course_continue",
    ),
    path(
        "lesson/<int:lesson_id>/navigate/",
        LessonNavigationView.as_view(),
        name="lesson_navigate",
    ),
    path("enroll/<slug:slug>/", EnrollView.as_view(), name="enroll_course"),
    path("enrollment/success/", EnrollmentSuccessView.as_view(), name="enrollment_success"),
    path("dashboard/payments/", PaymentHistoryView.as_view(), name="payment_history"),
] + payment_urls
